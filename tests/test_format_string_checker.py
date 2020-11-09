import pytest

from patterns.detect.format_string_checker import FormatStringChecker
from rparser import parse

params = [
    # From other repositories: https://github.com/usgs/warc-iridium-sbd-decoder/commit/505f5832c975be601acf9ccdfcd729e0134d79f7
    (True, FormatStringChecker(), 'VA_FORMAT_STRING_USES_NEWLINE', 'PseudobinaryBPayloadDecoder.java',
             "@@ -278,7 +278,7 @@ Status processLine(final List<String> p_Line,\n \t\tif (!findFirst.isPresent())\n \t\t{\n \t\t\tlog.warn(String.format(\n+\t\t\t\t\t\"No matching data type for (name: %s, units: %s) among:\\n - %s\",\n-\t\t\t\t\t\"No matching data type for (name: %s, units: %s) among:%n - %s\",\n \t\t\t\t\tname, units,\n \t\t\t\t\tp_DataTypes.stream()\n \t\t\t\t\t\t\t.map(type -> String.format(",
     1, 281),
    # From other repositories: https://github.com/jenkinsci/fortify-plugin/commit/c455799062f84d2d79a1c3f198816f73916d157d    (False, FindFinalizeInvocations(), 'VA_FORMAT_STRING_USES_NEWLINE', 'SutronStandardCsvPayloadDecoder.java',
    (True, FormatStringChecker(), 'VA_FORMAT_STRING_USES_NEWLINE', 'ProjectCreationService.java',
     "@@ -181,10 +181,10 @@ public Long createProject(ProjectDataEntry projectData) throws IOException, ApiE\n \t\t\t}\n \n \t\t\tif (issueTemplate != null) {\n+\t\t\t\tlogWriter.printf(\"Selected Issue Template is '%s'\\n\", issueTemplate.getName()); // Issue template found\n \t\t\t} else {\n \t\t\t\tissueTemplate = defaultIssueTemplate; // selected issue template is not valid so use default template\n+\t\t\t\tlogWriter.printf(\"Specified Issue Template ='%s' doesn't exist, template '%s' is used instead!\\n\",\n \t\t\t\t\t\tselectedIssueTemplateName, issueTemplate.getName());\n \t\t\t}\n \t\t}\n",
     2, 184),
    # DIY
    (True, FormatStringChecker(), 'VA_FORMAT_STRING_USES_NEWLINE', 'Fake.java',
     "@@ -58,7 +58,7 @@ public PseudobinaryBPayloadDecoder()\n \t\t\t\t\"Invalid payload type for this decoder.\");\n \n \t\tfinal byte[] payload = p_Payload.getPayload();\n+\t\tlog.info(String.format( Locale.US, \"Payload:\\n%s\", new String(payload))); \n \t\tfinal Queue<Byte> payloadQueue = Queues\n \t\t\t\t.newArrayBlockingQueue(payload.length);",
     1, 61),
    # DIY
    (True, FormatStringChecker(), 'VA_FORMAT_STRING_USES_NEWLINE', 'Fake.java',
     "@@ -280,7 +280,7 @@ private void setIntegerValue(final String projectAttributeValue,\n			value.setIntegerValue(Long.valueOf(projectAttributeValue));\n		} catch (NumberFormatException e) {\n			logWriter.printf(\"[WARN] Failed to set an integer value\\n\");",
     1, 282),
  ]

@pytest.mark.parametrize('is_patch,detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch:bool, detector, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0

