import pytest
from rparser import parse

params = [
    # -------------------------- test support for patch and non-patch --------------------------
    (True,
             '''@@ -1 +1,21 @@
             void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {

                 any.finalize();
             }''', 3),
    (False,
               '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
                   any.finalize();
               }''', 3),
    # test single-line comments
    (False,
       '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
           any.finalize(); // this is a single statement
       }''', 3),
    (False,
       '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
           // this is a single statement
           any.finalize();
           // this is a single statement
       }''', 3),
    (True,
       '''@@ -1,0 +1,0 @@
       void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
-    // this is a single statement
+    any.finalize();
+    // this is a single statement
}''', 3),
    # -------------------------- test multi-line comments --------------------------
    (False,
         '''@Override
        public void onReceive(final Context context, Intent intent) {
           /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
            mURL = dbhelper.Obt_url();
            if (mURL == ""){
                mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
                Log.i("SQLL","Url vacio");
            }else{
                Log.i("SQLL","Url cargado   "+mURL);
            }*/
            WebView gv = new WebView(context);''', 3),
    (True,
     '''@@ -1,0 +1,0 @@ @Override
    public void onReceive(final Context context, Intent intent) {
       /*  This is a multi-line comments
-       1st line
+       this is the first line
        This is the second line
-       This is the third line
        This is the final line
      */
      return false;''', 2),
    (True,
     '''@@ -2,0 +2,0 @@ @Override
    public void onReceive(final Context context, Intent intent) {
-       /*
        dbhelper = new DatabaseHandler(context, "RG", null, 1);
        mURL = dbhelper.Obt_url();
        if (mURL == ""){
            mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
            Log.i("SQLL","Url vacio");
        }else{
            Log.i("SQLL","Url cargado   "+mURL);
        }
-        */
        WebView gv = new WebView(context);''', 10),

    # -------------------------- test multi-line comments witout '*/' --------------------------
    (True, '''@@ -1,0 +1,0 @@
     /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
        mURL = dbhelper.Obt_url();
        if (mURL == ""){
            mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
+            Log.i("SQLL","Url vacio");
        }else{
        ''', 0),
    (True, '''@@ -1,0 +1,0 @@
-    /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
        mURL = dbhelper.Obt_url();
        if (mURL == ""){
            mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
+            Log.i("SQLL","Url vacio");
        }else{
        ''', 5),

    # -------------------------- test multi-line comments without '/*' --------------------------
    (True, '''@@ -1,0 +1,0 @@ /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
            mURL = dbhelper.Obt_url();
            if (mURL == ""){
                mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
                Log.i("SQLL","Url vacio");
            }else{
-                Log.i("SQLL","Url cargado   "+mURL);
+                Log.i("SQLL","Url cargado   "+mURL);} */
-            }*/
            WebView gv = new WebView(context);''', 1),
    (True, '''@@ -1,0 +1,0 @@ /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
            mURL = dbhelper.Obt_url();
            if (mURL == ""){
                mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
-               Log.i("SQLL","Url vacio");
+               Log.i("SQLL","Url vacio   "+mURL);
            }else{
                 Log.i("SQLL","Url cargado   "+mURL);
-           } */
+           }
            WebView gv = new WebView(context);''', 8),
    (True, '''@@ -1,0 +1,0 @@ /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
            mURL = dbhelper.Obt_url();
            if (mURL == ""){
                mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
-               Log.i("SQLL","Url vacio");
+               Log.i("SQLL","Url vacio   "+mURL);
            }else{
                 Log.i("SQLL","Url cargado   "+mURL);
            }
           */

            WebView gv = new WebView(context);''', 1),
    # switch case
    (False, '''switch (c) {
        case 'a':
        case 'A':
            if (csName == "ASCII" || equalEncodings(csName, "ASCII")) {
                return CS_US_ASCII;
            }
            break;

        case 'c':''', 8),
    ]


@pytest.mark.parametrize('is_patch,patch_str,expected_length', params)
def test_statement_length(is_patch:bool, patch_str: str, expected_length: int):
    patch = parse(patch_str, is_patch)
    assert len(patch.hunks[0].lines) == expected_length


def test_multi_hunks():
    patch = parse('''@@ -21,6 +21,7 @@
 import io.github.mzmine.datamodel.Frame;
 import io.github.mzmine.datamodel.featuredata.impl.SimpleIonMobilitySeries;
 import io.github.mzmine.datamodel.featuredata.impl.SummedIntensityMobilitySeries;
+import io.github.mzmine.util.MemoryMapStorage;
 import java.util.List;
 
 /**
@@ -43,4 +44,44 @@ default SimpleIonMobilitySeries getMobilogram(int index) {
   }
 
   SummedIntensityMobilitySeries getSummedMobilogram();
+
+  /**
+   * Creates a copy of this series using the same frame list, but with new mz/intensities and new
+   * mobilograms, e.g. after smoothing.
+   *
+   * @param storage
+   * @param newMzValues
+   * @param newIntensityValues
+   * @param newMobilograms
+   * @return
+   */
+  IonMobilogramTimeSeries copyAndReplace(MemoryMapStorage storage, double[] newMzValues,
+      double[] newIntensityValues, List<SimpleIonMobilitySeries> newMobilograms);
+
+  /**
+   * @param scan
+   * @return The intensity value for the given scan or 0 if the no intensity was measured at that
+   * scan.
+   */
+  @Override
+  default double getIntensityForSpectrum(Frame scan) {
+    int index = getSpectra().indexOf(scan);
+    if (index != -1) {
+      return getIntensity(index);
+    }
+    return 0;
+  }
+
+  /**
+   * @param scan
+   * @return The mz for the given scan or 0 if no intensity was measured at that scan.
+   */
+  @Override
+  default double getMzForSpectrum(Frame scan) {
+    int index = getSpectra().indexOf(scan);
+    if (index != -1) {
+      return getMZ(index);
+    }
+    return 0;
+  }
 }''')
    assert len(patch.hunks[0].lines) == 5
    assert len(patch.hunks[1].lines) == 20


def test_2():
    patch = parse('''@@ -44,39 +48,53 @@ public static OtpProjectInfo projectInfo() {
     OtpProjectInfo() {
         this(
             "0.0.0-ParseFailure",
-            new VersionControlInfo(
-                UNKNOWN,
-                UNKNOWN,
-                UNKNOWN,
-                UNKNOWN,
-                true
-            )
+            new GraphFileHeader(),
+            new VersionControlInfo()
         );
     }
     
     public OtpProjectInfo(
             String version,
+            GraphFileHeader graphFileHeaderInfo,
             VersionControlInfo versionControl
     ) {
         this.version = MavenProjectVersion.parse(version);
+        this.graphFileHeaderInfo = graphFileHeaderInfo;
         this.versionControl = versionControl;
     }
 
     public long getUID() {
         return hashCode();
     }
 
+    /**
+     * Return {@code true} if the graph file and the running instance of OTP is the
+     * same instance. If the running instance of OTP or the Graph.obj serialization id
+     * is unknown, then {@code true} is returned.
+     */
+    public boolean matchesRunningOTPInstance(GraphFileHeader graphFileHeader) {
+        if(graphFileHeader.isUnknown()) { return true; }
+        if(this.graphFileHeaderInfo.isUnknown()) { return true; }
+        return this.graphFileHeaderInfo.equals(graphFileHeader);
+    }
+
     public String toString() {
         return "OTP " + getVersionString();
     }
 
     /**
      * Return a version string:
-     * {@code version: 2.1.0, commit: 2121212.., branch: dev-2.x}
+     * {@code version: 2.1.0, graph-id: 00001, commit: 2121212.., branch: dev-2.x}
      */
     public String getVersionString() {
-        String format = "version: %s, commit: %s, branch: %s";
-        return String.format(format, version.version, versionControl.commit, versionControl.branch);
+        String format = "version: %s, graph-id: %s, commit: %s, branch: %s";
+        return String.format(
+            format,
+            version.version,
+            getExpectedGraphVersion(),
+            versionControl.commit,
+            versionControl.branch
+        );
     }
 
     /**
@@ -86,4 +104,10 @@ public String getVersionString() {
     public boolean sameVersion(OtpProjectInfo other) {
         return this.version.sameVersion(other.version);
     }
+
+    public String getExpectedGraphVersion() {
+        return graphFileHeaderInfo.isUnknown()
+            ? UNKNOWN
+            : graphFileHeaderInfo.serializationId();
+    }
 }''')
    assert len(patch.hunks[0].lines) == 27
    assert len(patch.hunks[1].lines) == 7


def test_03():
    patch = parse('''@@ -31,6 +31,16 @@ private Config(){}
     private static boolean manga;
     /** 送出即将过期礼物给此 up 的直播间 */
     private static String upLive;
+    /** 对于进行投币的视频选择是否点赞 */
-    /** test */
+    private static String selectLike;
+
+    public String getSelectLike() {
+        return selectLike;
+    }
+
+    public void setSelectLike(String selectLike) {
+        Config.selectLike = selectLike;
+    }
 
     public String getUpLive() {
         return upLive;''')
    assert len(patch.hunks[0].lines) == 11