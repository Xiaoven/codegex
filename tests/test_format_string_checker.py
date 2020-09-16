from patterns.detect.format_string_checker import FormatStringChecker
from rparser import Patch



class TestSerializableIdiom:

    # From other repositories: https://github.com/usgs/warc-iridium-sbd-decoder/commit/505f5832c975be601acf9ccdfcd729e0134d79f7
    def test_VA_FORMAT_STRING_USES_NEWLINE_01(self):
        patch = Patch()
        patch.name = "PseudobinaryBPayloadDecoder.java"
        patch.parse("@@ -58,7 +58,7 @@ public PseudobinaryBPayloadDecoder()\n				\"Invalid payload type for this decoder.\");\n\n		final byte[] payload = p_Payload.getPayload();\n+		log.info(String.format(\"Payload:\\n%s\", new String(payload)));\n\n		final Queue<Byte> payloadQueue = Queues")
        detector = FormatStringChecker()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1

    # From other repositories: https://github.com/usgs/warc-iridium-sbd-decoder/commit/505f5832c975be601acf9ccdfcd729e0134d79f7
    def test_VA_FORMAT_STRING_USES_NEWLINE_02(self):
        patch = Patch()
        patch.name = "SutronStandardCsvPayloadDecoder.java"
        patch.parse("@@ -278,7 +278,7 @@ Status processLine(final List<String> p_Line,\n \t\tif (!findFirst.isPresent())\n \t\t{\n \t\t\tlog.warn(String.format(\n+\t\t\t\t\t\"No matching data type for (name: %s, units: %s) among:\\n - %s\",\n-\t\t\t\t\t\"No matching data type for (name: %s, units: %s) among:%n - %s\",\n \t\t\t\t\tname, units,\n \t\t\t\t\tp_DataTypes.stream()\n \t\t\t\t\t\t\t.map(type -> String.format(")
        detector = FormatStringChecker()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1

    # From other repositories: https://github.com/jenkinsci/fortify-plugin/commit/c455799062f84d2d79a1c3f198816f73916d157d
    def test_VA_FORMAT_STRING_USES_NEWLINE_03(self):
        patch = Patch()
        patch.name = "ProjectCreationService.java"
        patch.parse("@@ -181,10 +181,10 @@ public Long createProject(ProjectDataEntry projectData) throws IOException, ApiE\n \t\t\t}\n \n \t\t\tif (issueTemplate != null) {\n+\t\t\t\tlogWriter.printf(\"Selected Issue Template is '%s'\\n\", issueTemplate.getName()); // Issue template found\n \t\t\t} else {\n \t\t\t\tissueTemplate = defaultIssueTemplate; // selected issue template is not valid so use default template\n+\t\t\t\tlogWriter.printf(\"Specified Issue Template ='%s' doesn't exist, template '%s' is used instead!\\n\",\n \t\t\t\t\t\tselectedIssueTemplateName, issueTemplate.getName());\n \t\t\t}\n \t\t}\n")
        detector = FormatStringChecker()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 2

    # DIY
    def test_VA_FORMAT_STRING_USES_NEWLINE_04(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse(
            "@@ -58,7 +58,7 @@ public PseudobinaryBPayloadDecoder()\n \t\t\t\t\"Invalid payload type for this decoder.\");\n \n \t\tfinal byte[] payload = p_Payload.getPayload();\n+\t\tlog.info(String.format( Locale.US, \"Payload:\\n%s\", new String(payload))); \n \t\tfinal Queue<Byte> payloadQueue = Queues\n \t\t\t\t.newArrayBlockingQueue(payload.length);")
        detector = FormatStringChecker()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1

    # DIY
    def test_VA_FORMAT_STRING_USES_NEWLINE_05(self):
        patch = Patch()
        patch.name = "ProjectCreationService.java"
        patch.parse("@@ -280,7 +280,7 @@ private void setIntegerValue(final String projectAttributeValue,\n			value.setIntegerValue(Long.valueOf(projectAttributeValue));\n		} catch (NumberFormatException e) {\n			logWriter.printf(\"[WARN] Failed to set an integer value\\n\");")
        detector = FormatStringChecker()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
