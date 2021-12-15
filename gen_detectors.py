from patterns.detect.URL_problems import URLCollectionDetector
from patterns.detect.bad_syntax_for_regular_expression import SingleDotPatternDetector, FileSeparatorAsRegexpDetector
from patterns.detect.find_dead_local_stores import FindDeadLocalIncrementInReturn
from patterns.detect.find_puzzlers import BadMonthDetector, ShiftAddPriorityDetector, ReuseEntryInIteratorDetector, \
    MultiplyIRemResultDetector, AnonymousArrayToStringDetector
from patterns.detect.find_self_comparison import CheckForSelfComputation, CheckForSelfComparison
from patterns.detect.incompat_mask import IncompatMaskDetector
from patterns.detect.inheritance_unsafe_get_resource import GetResourceDetector
from patterns.detect.questionable_boolean_assignment import BooleanAssignmentDetector
from patterns.detect.static_calendar_detector import StaticDateFormatDetector
from patterns.detect.method_return_check import NotThrowDetector
from patterns.detect.overriding_equals_not_symmetrical import EqualsClassNameDetector
from patterns.detect.infinite_recursive_loop import CollectionAddItselfDetector
from patterns.detect.find_rough_constants import FindRoughConstantsDetector
from patterns.detect.find_ref_comparison import EqualityDetector, CallToNullDetector
from patterns.detect.naming import SimpleSuperclassNameDetector, SimpleInterfaceNameDetector, HashCodeNameDetector, \
    ToStringNameDetector, EqualNameDetector, ExceptionClassNameDetector
from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod, DefPrivateMethod
from patterns.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from patterns.detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, \
    StringCtorDetector, InvalidMinMaxDetector, VacuousEasyMockCallDetector, BigDecimalConstructorDetector, \
    NonsensicalInvocationDetector, BooleanCtorDetector, NumberCTORDetector, FPNumberCTORDetector, \
    BoxedPrimitiveToStringDetector, BoxedPrimitiveForParsingDetector
from patterns.detect.format_string_checker import NewLineDetector
from patterns.detect.find_float_equality import FloatEqualityDetector
from patterns.detect.find_puzzlers import OverwrittenIncrementDetector
from patterns.detect.find_bad_cast import FindBadCastDetector
from patterns.detect.naming import ClassNameConventionDetector, MethodNameConventionDetector
from patterns.detect.dont_use_enum import DontUseEnumDetector
from patterns.detect.find_self_assignment import CheckForSelfAssignment, CheckForSelfDoubleAssignment
from patterns.detect.synchronize_on_class_literal_not_get_class import SynGetClassDetector
from patterns.detect.volatile_usage import VolatileArrayDetector
from patterns.detect.wait_in_loop import NotifyDetector
from patterns.detect.dumb_method_invocations import UselessSubstringDetector
from patterns.detect.bad_use_of_return_value import DontJustCheckReadlineDetector

DETECTOR_DICT = {
    "IncompatMaskDetector": IncompatMaskDetector,
    "GetResourceDetector": GetResourceDetector,
    "StaticDateFormatDetector": StaticDateFormatDetector,
    "NotThrowDetector": NotThrowDetector,
    "EqualsClassNameDetector": EqualsClassNameDetector,
    "CollectionAddItselfDetector": CollectionAddItselfDetector,
    "FindRoughConstantsDetector": FindRoughConstantsDetector,
    "EqualityDetector": EqualityDetector,
    "CallToNullDetector": CallToNullDetector,
    "SimpleSuperclassNameDetector": SimpleSuperclassNameDetector,
    "SimpleInterfaceNameDetector": SimpleInterfaceNameDetector,
    "HashCodeNameDetector": HashCodeNameDetector,
    "ToStringNameDetector": ToStringNameDetector,
    "DontCatchIllegalMonitorStateException": DontCatchIllegalMonitorStateException,
    "ExplicitInvDetector": ExplicitInvDetector,
    "PublicAccessDetector": PublicAccessDetector,
    "DefSerialVersionID": DefSerialVersionID,
    "DefReadResolveMethod": DefReadResolveMethod,
    "SuspiciousCollectionMethodDetector": SuspiciousCollectionMethodDetector,
    "FinalizerOnExitDetector": FinalizerOnExitDetector,
    "RandomOnceDetector": RandomOnceDetector,
    "RandomD2IDetector": RandomD2IDetector,
    "StringCtorDetector": StringCtorDetector,
    "NewLineDetector": NewLineDetector,
    "InvalidMinMaxDetector":  InvalidMinMaxDetector,
    'CheckForSelfComputation': CheckForSelfComputation,
    'CheckForSelfComparison': CheckForSelfComparison,
    'FindDeadLocalIncrementInReturn': FindDeadLocalIncrementInReturn,
    "DefPrivateMethod": DefPrivateMethod,
    'EqualNameDetector': EqualNameDetector,
    'BooleanAssignmentDetector': BooleanAssignmentDetector,
    'BadMonthDetector': BadMonthDetector,
    'ShiftAddPriorityDetector': ShiftAddPriorityDetector,
    'FloatEqualityDetector': FloatEqualityDetector,
    'FindBadCastDetector': FindBadCastDetector,
    'OverwrittenIncrementDetector': OverwrittenIncrementDetector,
    'SingleDotPatternDetector': SingleDotPatternDetector,
    'FileSeparatorAsRegexpDetector': FileSeparatorAsRegexpDetector,
    'ClassNameConventionDetector': ClassNameConventionDetector,
    'MethodNameConventionDetector': MethodNameConventionDetector,
    'DontUseEnumDetector': DontUseEnumDetector,
    'CheckForSelfAssignment': CheckForSelfAssignment,
    'CheckForSelfDoubleAssignment': CheckForSelfDoubleAssignment,
    'ExceptionClassNameDetector': ExceptionClassNameDetector,
    'ReuseEntryInIteratorDetector': ReuseEntryInIteratorDetector,
    'VacuousEasyMockCallDetector': VacuousEasyMockCallDetector,
    'BigDecimalConstructorDetector': BigDecimalConstructorDetector,
    'NonsensicalInvocationDetector': NonsensicalInvocationDetector,
    'MultiplyIRemResultDetector': MultiplyIRemResultDetector,
    'AnonymousArrayToStringDetector': AnonymousArrayToStringDetector,
    'VolatileArrayDetector': VolatileArrayDetector,
    'SynGetClassDetector': SynGetClassDetector,
    'NotifyDetector': NotifyDetector,
    'URLCollectionDetector': URLCollectionDetector,
    'BooleanCtorDetector': BooleanCtorDetector,
    'NumberCTORDetector': NumberCTORDetector,
    'FPNumberCTORDetector': FPNumberCTORDetector,
    'BoxedPrimitiveToStringDetector': BoxedPrimitiveToStringDetector,
    'BoxedPrimitiveForParsingDetector': BoxedPrimitiveForParsingDetector,
    'UselessSubstringDetector': UselessSubstringDetector,
    'DontJustCheckReadlineDetector': DontJustCheckReadlineDetector,
}