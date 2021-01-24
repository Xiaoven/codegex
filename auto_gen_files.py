import re
import os

all_pattern_set = set(['CNT_ROUGH_CONSTANT_VALUE', 'NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'NM_FUTURE_KEYWORD_USED_AS_METHOD_IDENTIFIER',
                'IMSE_DONT_CATCH_IMSE', 'DM_EXIT', 'DM_RUN_FINALIZERS_ON_EXIT', 'FI_EXPLICIT_INVOCATION', 'ES_COMPARING_STRINGS_WITH_EQ',
                'SE_NONFINAL_SERIALVERSIONID', 'SE_NONSTATIC_SERIALVERSIONID', 'SE_NONLONG_SERIALVERSIONID', 'RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN',
                'VA_FORMAT_STRING_USES_NEWLINE', 'BIT_SIGNED_CHECK', 'DMI_RANDOM_USED_ONLY_ONCE', 'DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION',
                'UI_INHERITANCE_UNSAFE_GETRESOURCE', 'JCIP_FIELD_ISNT_FINAL_IN_IMMUTABLE_CLASS', 'NM_SAME_SIMPLE_NAME_AS_SUPERCLASS',
                'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'EQ_GETCLASS_AND_CLASS_CONSTANT', 'NM_METHOD_NAMING_CONVENTION', 'NM_FIELD_NAMING_CONVENTION',
                'NM_CLASS_NAMING_CONVENTION', 'IL_CONTAINER_ADDED_TO_ITSELF', 'RV_01_TO_INT', 'DM_INVALID_MIN_MAX', 'EQ_COMPARING_CLASS_NAMES',
                'NM_LCASE_HASHCODE', 'NM_LCASE_TOSTRING', 'NM_BAD_EQUAL', 'SE_READ_RESOLVE_IS_STATIC', 'SE_READ_RESOLVE_MUST_RETURN_OBJECT',
                'RV_EXCEPTION_NOT_THROWN', 'EC_NULL_ARG', 'BIT_AND', 'BIT_IOR', 'BIT_AND_ZZ', 'SA_LOCAL_SELF_ASSIGNMENT_INSTEAD_OF_FIELD',
                'SA_SELF_ASSIGNMENT', 'SA_SELF_COMPUTATION', 'SA_SELF_COMPUTATION', 'SA_SELF_COMPARISON',
                'SA_SELF_COMPARISON', 'SA_SELF_ASSIGNMENT', 'SA_DOUBLE_ASSIGNMENT', 'SA_DOUBLE_ASSIGNMENT',
                'DLS_DEAD_LOCAL_INCREMENT_IN_RETURN', 'FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER', 'BC_IMPOSSIBLE_DOWNCAST_OF_TOARRAY',
                'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_CANT_USE_FILE_SEPARATOR_AS_REGULAR_EXPRESSION', 'DLS_OVERWRITTEN_INCREMENT',
                'BSHIFT_WRONG_ADD_PRIORITY', 'IM_MULTIPLYING_RESULT_OF_IREM', 'DMI_BAD_MONTH', 'QBA_QUESTIONABLE_BOOLEAN_ASSIGNMENT',
                'DMI_VACUOUS_SELF_COLLECTION_CALL', 'DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES', 'SE_METHOD_MUST_BE_PRIVATE',
                'RE_BAD_SYNTAX_FOR_REGULAR_EXPRESSION', 'STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE', 'STCAL_STATIC_CALENDAR_INSTANCE',
                          'DM_STRING_CTOR', 'DM_STRING_VOID_CTOR', 'FI_PUBLIC_SHOULD_BE_PROTECTED', 'BIT_SIGNED_CHECK_HIGH_BIT'])

def snake_to_camel(word):
    return ''.join(x.capitalize() for x in word.split('_'))


if __name__ == '__main__':
    p_detector = re.compile(r'class\s*([^\s()]+)\(Detector\)')
    p = re.compile(r'[\'"]([A-Z0-9]+_+[A-Z_0-9]+)[\'"]')
    detector_path = os.path.join(os.getcwd(), 'patterns/detect')
    done_pattern_set = set()
    file_names = list()
    detector_names = list()
    import_list = list()

    for filename in os.listdir(detector_path):
        path = os.path.join(detector_path, filename)
        if not os.path.isfile(path):
            continue

        strip_filename = filename[:-3]   # Remove '.py'

        camel_name = snake_to_camel(strip_filename)
        file_names.append(camel_name)

        import_stmt = None

        with open(path, 'r') as f:
            content = f.read()
            pattern_list = p.findall(content)
            if pattern_list:
                done_pattern_set.update(pattern_list)

            detectors = p_detector.findall(content)
            if detectors:
                tmp_str = ', '.join(detectors)
                import_stmt = f'from patterns.detect.{strip_filename} import {tmp_str}\n'
                for name in detectors:
                    detector_names.append(f'"{name}": {name}')

        if import_stmt:
            import_list.append(import_stmt)

    print('[Length of file names]', len(file_names))
    print('[Number of completed patterns]', len(done_pattern_set))
    print('[Number of all patterns]', len(all_pattern_set))
    print('[Number of uncompleted patterns]', len(all_pattern_set.symmetric_difference(done_pattern_set)), all_pattern_set.symmetric_difference(done_pattern_set))
    print('[Number of Detectors]', len(detector_names))

    with open('gen_detectors.py', 'w') as f:
        if import_list:
            f.writelines(import_list)
        if detector_names:
            f.write('\nDETECTOR_DICT = {\n    ' + ',\n    '.join(detector_names) + '\n}')

    # with open('spotbugs-includeFilter.xml', 'w') as f:
    #     f.write('<FindBugsFilter>\n')
    #     for pattern in all_pattern_set:
    #         f.write(f'\t<Match>\n\t\t<Bug pattern="{pattern}"/>\n\t</Match>\n')
    #     f.write('</FindBugsFilter>')
