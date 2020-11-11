import pytest
from rparser import parse

params = [
    # test support for patch and non-patch
#     (True,
#              '''@@ -1 +1,21 @@
#              void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
#                  any.finalize();
#              }''', 3),
#     (False,
#                '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
#                    any.finalize();
#                }''', 3),
#     # test single-line comments
#     (False,
#        '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
#            any.finalize(); // this is a single statement
#        }''', 3),
#     (False,
#        '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
#            // this is a single statement
#            any.finalize();
#            // this is a single statement
#        }''', 5),
#     (True,
#        '''@@ -1,0 +1,0 @@
#        void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
# -    // this is a single statement
# +    any.finalize();
# +    // this is a single statement
# }''', 5),
    # test multi-line comments
    (True,
         '''@@ -1,0 +1,0 @@
         @Override
        public void onReceive(final Context context, Intent intent) {
           /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
            mURL = dbhelper.Obt_url();
            if (mURL == ""){
                mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
                Log.i("SQLL","Url vacio");
            }else{
                Log.i("SQLL","Url cargado   "+mURL);
            }*/
            WebView gv = new WebView(context);''', 4),
    (True,
         '''@@ -1,0 +1,0 @@ /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
            mURL = dbhelper.Obt_url();
            if (mURL == ""){
                mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
                Log.i("SQLL","Url vacio");
            }else{
                Log.i("SQLL","Url cargado   "+mURL);
            }*/
            WebView gv = new WebView(context);''', 2),
]

@pytest.mark.parametrize('is_patch,patch_str,expected_length', params)
def test_statement_length(is_patch:bool, patch_str: str, expected_length: int):
    patch = parse(patch_str, is_patch)
    assert len(patch.hunks[0].lines) == expected_length
