import pytest

from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    # https://github.com/qiniu/android-sdk/pull/453
    (True, 'SA_SELF_COMPUTATION', 'main.java',
     '''@@ -4,7 +4,9 @@ package com.qiniu.android.http.request;\n import com.qiniu.android.collect.ReportItem;\n import com.qiniu.android.collect.UploadInfoReporter;\n import com.qiniu.android.http.ResponseInfo;\n +import com.qiniu.android.http.connectCheck.ConnectChecker;\n import com.qiniu.android.http.dns.DnsPrefetcher;\n +import com.qiniu.android.http.networkStatus.NetworkStatusManager;\n import com.qiniu.android.http.request.httpclient.SystemHttpClient;\n import com.qiniu.android.http.request.handler.CheckCancelHandler;\n import com.qiniu.android.http.request.handler.RequestProgressHandler;\n @@ -13,8 +15,8 @@ import com.qiniu.android.http.metrics.UploadSingleRequestMetrics;\n import com.qiniu.android.storage.Configuration;\n import com.qiniu.android.storage.UpToken;\n import com.qiniu.android.storage.UploadOptions;\n -import com.qiniu.android.utils.AsyncRun;\n import com.qiniu.android.utils.LogUtil;\n +import com.qiniu.android.utils.StringUtils;\n import com.qiniu.android.utils.Utils;\n \n import org.json.JSONObject;\n @@ -31,7 +33,7 @@ class HttpSingleRequest {\n private final UploadRequestInfo requestInfo;\n private final UploadRequestState requestState;\n \n -    private ArrayList <UploadSingleRequestMetrics> requestMetricsList;\n +    private ArrayList<UploadSingleRequestMetrics> requestMetricsList;\n \n private IRequestClient client;\n \n @@ -45,28 +47,26 @@ class HttpSingleRequest {\n this.token = token;\n this.requestInfo = requestInfo;\n this.requestState = requestState;\n -        this.currentRetryTime = 1;\n +        this.currentRetryTime = 0;\n }\n \n void request(Request request,\n boolean isAsync,\n -                 boolean toSkipDns,\n RequestShouldRetryHandler shouldRetryHandler,\n RequestProgressHandler progressHandler,\n -                 RequestCompleteHandler completeHandler){\n -        currentRetryTime = 1;\n +                 RequestCompleteHandler completeHandler) {\n +        currentRetryTime = 0;\n requestMetricsList = new ArrayList<>();\n -        retryRequest(request, isAsync, toSkipDns, shouldRetryHandler, progressHandler, completeHandler);\n +        retryRequest(request, isAsync, shouldRetryHandler, progressHandler, completeHandler);\n }\n \n private void retryRequest(final Request request,\n final boolean isAsync,\n -                              final boolean toSkipDns,\n final RequestShouldRetryHandler shouldRetryHandler,\n final RequestProgressHandler progressHandler,\n -                              final RequestCompleteHandler completeHandler){\n +                              final RequestCompleteHandler completeHandler) {\n \n -        if (toSkipDns){\n +        if (request.uploadServer.isHttp3()) {\n client = new SystemHttpClient();\n } else {\n client = new SystemHttpClient();\n @@ -76,41 +76,60 @@ class HttpSingleRequest {\n @Override\n public boolean checkCancel() {\n boolean isCancelled = requestState.isUserCancel();\n -                if (! isCancelled && uploadOption.cancellationSignal != null) {\n +                if (!isCancelled && uploadOption.cancellationSignal != null) {\n isCancelled = uploadOption.cancellationSignal.isCancelled();\n }\n return isCancelled;\n }\n };\n \n +        LogUtil.i(\"key:\" + StringUtils.toNonnullString(requestInfo.key) +\n +                \" retry:\" + currentRetryTime +\n +                \" url:\" + StringUtils.toNonnullString(request.urlString) +\n +                \" ip:\" + StringUtils.toNonnullString(request.ip));\n +\n client.request(request, isAsync, config.proxy, new IRequestClient.RequestClientProgress() {\n @Override\n public void progress(long totalBytesWritten, long totalBytesExpectedToWrite) {\n if (checkCancelHandler.checkCancel()) {\n requestState.setUserCancel(true);\n -                    if (client != null){\n +                    if (client != null) {\n client.cancel();\n }\n -                } else if (progressHandler != null){\n +                } else if (progressHandler != null) {\n progressHandler.progress(totalBytesWritten, totalBytesExpectedToWrite);\n }\n }\n }, new IRequestClient.RequestClientCompleteHandler() {\n @Override\n public void complete(ResponseInfo responseInfo, UploadSingleRequestMetrics metrics, JSONObject response) {\n -                if (metrics != null){\n +                if (metrics != null) {\n requestMetricsList.add(metrics);\n }\n +\n +                if (shouldCheckConnect(responseInfo)) {\n +                    UploadSingleRequestMetrics checkMetrics = ConnectChecker.check();\n +                    if (metrics != null) {\n +                        metrics.connectCheckMetrics = checkMetrics;\n +                    }\n +                    if (!ConnectChecker.isConnected(checkMetrics)) {\n +                        String message = \"check origin statusCode:\" + responseInfo.statusCode + \" error:\" + responseInfo.error;\n +                        responseInfo = ResponseInfo.errorInfo(ResponseInfo.NetworkSlow, message);\n +                    }\n +                }\n +\n +                LogUtil.i(\"key:\" + StringUtils.toNonnullString(requestInfo.key) +\n +                        \" response:\" + StringUtils.toNonnullString(responseInfo));\n if (shouldRetryHandler != null && shouldRetryHandler.shouldRetry(responseInfo, response)\n -                    && currentRetryTime < config.retryMax\n -                    && responseInfo.couldHostRetry()){\n +                        && currentRetryTime < config.retryMax\n +                        && responseInfo.couldHostRetry()) {\n currentRetryTime += 1;\n \n try {\n Thread.sleep(config.retryInterval);\n } catch (InterruptedException ignored) {\n }\n -                    retryRequest(request, isAsync, toSkipDns, shouldRetryHandler, progressHandler, completeHandler);\n +                    retryRequest(request, isAsync, shouldRetryHandler, progressHandler, completeHandler);\n } else {\n completeAction(request, responseInfo, response, metrics, completeHandler);\n }\n @@ -119,6 +138,16 @@ class HttpSingleRequest {\n \n }\n \n +    private boolean shouldCheckConnect(ResponseInfo responseInfo) {\n +        return responseInfo != null &&\n +                (responseInfo.statusCode == ResponseInfo.NetworkError || /* network error */\n +                        responseInfo.statusCode == -1001 || /* timeout */\n +                        responseInfo.statusCode == -1003 || /* unknown host */\n +                        responseInfo.statusCode == -1004 || /* cannot connect to host */\n +                        responseInfo.statusCode == -1005 || /* connection lost */\n +                        responseInfo.statusCode == -1009 || /* not connected to host */\n +                        responseInfo.isTlsError());\n +    }\n \n private synchronized void completeAction(Request request,\n ResponseInfo responseInfo,\n @@ -126,29 +155,46 @@ class HttpSingleRequest {\n UploadSingleRequestMetrics requestMetrics,\n RequestCompleteHandler completeHandler) {\n \n -        if (client == null){\n +        if (client == null) {\n return;\n }\n client = null;\n \n -        if (completeHandler != null){\n +        updateHostNetworkStatus(responseInfo, request.uploadServer, requestMetrics);\n +        reportRequest(responseInfo, request, requestMetrics);\n +\n +        if (completeHandler != null) {\n completeHandler.complete(responseInfo, requestMetricsList, response);\n }\n -        reportRequest(responseInfo, request, requestMetrics);\n +    }\n +\n +    private void updateHostNetworkStatus(ResponseInfo responseInfo, IUploadServer server, UploadSingleRequestMetrics requestMetrics) {\n +        if (requestMetrics == null) {\n +            return;\n +        }\n +        long byteCount = requestMetrics.bytesSend();\n +        if (requestMetrics.startDate != null && requestMetrics.endDate != null && byteCount > 1024 * 1024) {\n +            double second = requestMetrics.endDate.getTime() - requestMetrics.endDate.getTime();\n +            if (second > 0) {\n +                int speed = (int) (byteCount * 1000 / second);\n +                String type = Utils.getIpType(server.getIp(), server.getHost());\n +                NetworkStatusManager.getInstance().updateNetworkStatus(type, speed);\n +            }\n +        }\n }\n \n private void reportRequest(ResponseInfo responseInfo,\n Request request,\n -                               UploadSingleRequestMetrics requestMetrics){\n +                               UploadSingleRequestMetrics requestMetrics) {\n \n -        if (requestInfo == null || !requestInfo.shouldReportRequestLog() || requestMetrics == null){\n +        if (token == null || !token.isValid() || requestInfo == null || !requestInfo.shouldReportRequestLog() || requestMetrics == null) {\n return;\n }\n \n long currentTimestamp = Utils.currentTimestamp();\n ReportItem item = new ReportItem();\n item.setReport(ReportItem.LogTypeRequest, ReportItem.RequestKeyLogType);\n -        item.setReport((currentTimestamp/1000), ReportItem.RequestKeyUpTime);\n +        item.setReport((currentTimestamp / 1000), ReportItem.RequestKeyUpTime);\n item.setReport(ReportItem.requestReportStatusCode(responseInfo), ReportItem.RequestKeyStatusCode);\n item.setReport(responseInfo != null ? responseInfo.reqId : null, ReportItem.RequestKeyRequestId);\n item.setReport(request != null ? request.host : null, ReportItem.RequestKeyHost);\n 
     ''', 1, 177),
    # https://github.com/mhagnumdw/bean-info-generator/pull/5/files#diff-71bf0b35fa483782180f548a1a7d6cc4b3822ed12aa4bb86640f80dde9df3077R13
    (False, 'SA_SELF_COMPUTATION', 'Ideas_2013_11_06.java ',
     '''@NoWarning("SA_FIELD_SELF_COMPUTATION")
        public int testUpdate() {
            return flags ^(short) flags;
        }''', 0, 0),
    # https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/SelfFieldOperation.java#L25
    (False, 'SA_SELF_COMPUTATION', 'SelfFieldOperation_01.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON,SA_FIELD_SELF_COMPUTATION")
        int f() {
            if (x < x)
                x = (int) ( y ^ y);
            if (x != x)
                y = x | x;
            if (x >= x)
                x = (int)(y & y);
            if (y > y)
                y = x - x;
            return x;
        }''', 8, 4),
    # DIY
    (False, 'SA_SELF_COMPUTATION', 'DIY_01.java',
     '''return capabilities.level - level;''', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_02.java',
     '    $(".lolkek").shouldNotBe(and("visible&visible", visible, visible));    // visible&visible', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_03.java',
     'final AtomicReference<String> latest = new AtomicReference<>("2015-01-01-00-00-00");', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_04.java',
     'long expectUnacked = msgOutCounter - (i - i % cumulativeInterval);', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_05.java',
     ' return i | i & j;', 0, 0),
    # https://github.com/Vardan2020/VardanHomeWork/pull/20/files
    (False, 'SA_SELF_COMPUTATION', 'VardanHomeWork.java',
     'if (a > b & b>c) {', 0, 0),
    # https://github.com/oracle/graal/pull/3183/files
    (False, 'SA_SELF_COMPUTATION', 'graal.java',
     'int imm5Encoding = (index << eSize.bytes() | eSize.bytes()) << ASIMDImm5Offset;', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_06.java',
     'immTwice = immTwice | immTwice << 32;', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_07.java',
     'return i | j & j;', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_08.java',
     'return i | j & j | z;', 0, 0),
    (False, 'SA_SELF_COMPUTATION', 'DIY_09.java',
     'double second = requestMetrics.endDate.getTime() - requestMetrics.endDate.getTime();', 0, 0),
    # ---------------- SA_SELF_COMPARISON ----------------------
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation_02.java',
     '''@NoWarning("SA_FIELD_SELF_COMPARISON")
        public boolean test() {
            boolean result = false;
            result |= flags == (short) flags;
            result |= flags == (char) flags;
            result |= flags == (byte) flags;
            return result;
        }''', 0, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation_03.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON")
        public boolean testTP() {
            boolean result = false;
            result |= flags == flags;
            return result;
        }''', 1, 4),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation_04.java',
     '''@ExpectWarning(value="SA_FIELD_SELF_COMPARISON", confidence = Confidence.LOW)
    boolean volatileFalsePositive() {
        return z == z;
    }''', 1, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation_05.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON")
        boolean e() {
            return a.equals(a);
        }''', 1, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation_06.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON")
        int c() {
            return a.compareTo(a);
        }
    ''', 1, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation_07.java',
     ''' Objects.equals(requestCount, throttlingPolicy.requestCount) &&
         Objects.equals(unitTime, throttlingPolicy.unitTime) &&
         Objects.equals(timeUnit, throttlingPolicy.timeUnit) &&
         Objects.equals(tierPlan, throttlingPolicy.tierPlan) &&
         Objects.equals(stopOnQuotaReach, throttlingPolicy.stopOnQuotaReach) &&
         Objects.equals(monetizationProperties, throttlingPolicy.monetizationProperties);''', 0, 0),
    #  https://github.com/google/ExoPlayer/pull/8462
    (False, 'SA_SELF_COMPARISON', 'Fake_01.java',
    'if (capabilities.profile == profile && capabilities.level >= level) { ', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_02.java', 'private <T> T triggerBeforeConvert(T aggregateRoot) {', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_03.java',
     'public <C, R> R accept(AnalyzedStatementVisitor<C, R> analyzedStatementVisitor, C context) {', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_04.java',
     'public <T> T unwrap(String wrappingToken, Class<T> resultClass) {', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_05.java',
     'private <T> T exec(HttpRequest<Buffer> request, Object body, Class<T> resultClass, int expectedCode) {', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_06.java',
     'ArrayList<ArrayList<RecyclerView.ViewHolder>> mAdditionsList = new ArrayList<>();', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_07.java',
     '''private static final List<String> STEP_NAMES = Arrays.asList("Given a \\"stock\\" of symbol <symbol> and a threshold <threshold>",
                        "When the stock is traded at price <price>",
                        "Then the alert status should be status <status>"
        );''', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_08.java',
     'private static final List<String> STEP_NAMES = Arrays.asList("Given a stock of symbol <symbol> and a threshold <threshold>', 0, 0),
    # https://github.com/PowerOlive/Mysplash/pull/1/files
    (False, 'SA_SELF_COMPARISON', 'Mysplash.java',
     'return newModel instanceof AppObject && ((AppObject) newModel).iconId == iconId;', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_09.java',
     'if (disjunction.get(t).variable == variable)', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_10.java',
     'if (this.matriz[fila][col].valor == valor){', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_11.java',
     "if (email.length()-email.indexOf('.')-1 <= 1){", 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_12.java',
     "if (c >= c*b){", 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_13.java',
     'await().atMost(atMost, TimeUnit.SECONDS).until(() -> tmpDir.toFile().listFiles().length == length);', 0, 0),
    # https://github.com/DurankGts/CodenameOne/pull/40/files
    (False, 'SA_SELF_COMPARISON', 'CodenameOne.java',
     'mergeMode = inputPath.contains(",") || mergedFile != null;', 0, 0),
    # https://github.com/sunjincheng121/incubator-iotdb/blob/9d40954fdcbe67bf20fed063208b31b23d5650dd/cli/src/main/java/org/apache/iotdb/tool/ExportCsv.java#L343
    (False, 'SA_SELF_COMPARISON', 'incubator_iotdb.java',
     '} else if (value.contains(",")) {', 0, 0),
    # https://github.com/biojava/biojava/blob/master/biojava-ontology/src/main/java/org/biojava/nbio/ontology/utils/AbstractAnnotation.java#L236
    (False, 'SA_SELF_COMPARISON', 'biojava/AbstractAnnotation.java',
     'return ((Annotation) o).asMap().equals(asMap());', 0, 0),
    # https://github.com/micromata/projectforge/blob/develop/projectforge-wicket/src/main/java/org/projectforge/web/task/TaskTreeProvider.java#L198
    (False, 'SA_SELF_COMPARISON', 'biojava/AbstractAnnotation.java',
     'return ((TaskNodeModel) obj).id.equals(id);', 0, 0),
    (False, 'SA_SELF_COMPARISON', 'Fake_14.java',
     '"abc".equals("abc");', 1, 1),
    (False, 'SA_SELF_COMPARISON', 'asmsupport/ClassReader.java',
     'if (attrs[i].type.equals(type)) {}', 0, 0),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    engine = DefaultEngine(Context(), included_filter=['CheckForSelfComputation', 'CheckForSelfComparison'])
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
