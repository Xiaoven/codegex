import pytest

from codegex.models.context import Context
from codegex.models.engine import DefaultEngine
from codegex.utils.rparser import parse


params = [
    # https://github.com/frtu/governance-toolbox/commit/73ba78e1749f5f52338ae4802ddf9caa5680dcb5
    (True, 'DMI_COLLECTION_OF_URLS', 'frtu/governance-toolbox/ClassloaderUtil.java',
        """@@ -19,23 +21,28 @@
    private static final org.slf4j.Logger logger = org.slf4j.LoggerFactory.getLogger(ClassloaderUtil.class);

    public static void reloadClassloader(List<String> classpathElements) {
        try {
            Set<URL> urls = new HashSet<URL>();
            for (String element : classpathElements) {
                URL url = new File(element).toURI().toURL();
                urls.add(url);
                logger.debug("Add to url list:{}", urls);
            }""", 1, 25),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name

    engine = DefaultEngine(Context(), included_filter=['URLCollectionDetector'])
    engine.visit(patch)

    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0