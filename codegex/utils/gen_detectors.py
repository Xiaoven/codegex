from codegex.detect.URL_problems import URLCollectionDetector
from codegex.detect.bad_syntax_for_regular_expression import SingleDotPatternDetector, FileSeparatorAsRegexpDetector
from codegex.detect.find_dead_local_stores import FindDeadLocalIncrementInReturn
from codegex.detect.find_puzzlers import BadMonthDetector, ShiftAddPriorityDetector, ReuseEntryInIteratorDetector, \
    MultiplyIRemResultDetector, AnonymousArrayToStringDetector
from codegex.detect.find_self_comparison import CheckForSelfComputation, CheckForSelfComparison
from codegex.detect.incompat_mask import IncompatMaskDetector
from codegex.detect.inheritance_unsafe_get_resource import GetResourceDetector
from codegex.detect.number_constructor import NumberCTORDetector, FPNumberCTORDetector
from codegex.detect.questionable_boolean_assignment import BooleanAssignmentDetector
from codegex.detect.static_calendar_detector import StaticDateFormatDetector
from codegex.detect.method_return_check import NotThrowDetector
from codegex.detect.overriding_equals_not_symmetrical import EqualsClassNameDetector
from codegex.detect.infinite_recursive_loop import CollectionAddItselfDetector
from codegex.detect.find_rough_constants import FindRoughConstantsDetector
from codegex.detect.find_ref_comparison import EqualityDetector, CallToNullDetector
from codegex.detect.naming import SimpleSuperclassNameDetector, SimpleInterfaceNameDetector, HashCodeNameDetector, \
    ToStringNameDetector, EqualNameDetector, ExceptionClassNameDetector
from codegex.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from codegex.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from codegex.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod, DefPrivateMethod
from codegex.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from codegex.detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, \
    StringCtorDetector, InvalidMinMaxDetector, VacuousEasyMockCallDetector, BigDecimalConstructorDetector, \
    NonsensicalInvocationDetector, BooleanCtorDetector, BoxedPrimitiveToStringDetector, \
    BoxedPrimitiveForParsingDetector, BoxedPrimitiveForCompareDetector
from codegex.detect.format_string_checker import NewLineDetector
from codegex.detect.find_float_equality import FloatEqualityDetector
from codegex.detect.find_puzzlers import OverwrittenIncrementDetector
from codegex.detect.find_bad_cast import FindBadCastDetector
from codegex.detect.naming import ClassNameConventionDetector, MethodNameConventionDetector
from codegex.detect.dont_use_enum import DontUseEnumDetector
from codegex.detect.find_self_assignment import CheckForSelfAssignment, CheckForSelfDoubleAssignment
from codegex.detect.synchronize_on_class_literal_not_get_class import SynGetClassDetector
from codegex.detect.volatile_usage import VolatileArrayDetector
from codegex.detect.wait_in_loop import NotifyDetector
from codegex.detect.dumb_method_invocations import UselessSubstringDetector, IsAbsoluteFileNameDetector
from codegex.detect.dumb_methods import NewForGetclassDetector, NextIntViaNextDoubleDetector
from codegex.detect.find_useless_control_flow import UselessControlFlowNextLineDetector
from codegex.detect.inefficient_index_of import InefficientIndexOfDetector
from codegex.detect.bad_use_of_return_value import DontJustCheckReadlineDetector
from codegex.detect.dumb_method_invocations import UselessSubstringDetector
from codegex.detect.find_puzzlers import BoxingImmediatelyUnboxedDetector
from codegex.detect.dumb_methods import ImmediateDereferenceOfReadlineDetector


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
    'BoxedPrimitiveForCompareDetector': BoxedPrimitiveForCompareDetector,
    'UselessSubstringDetector': UselessSubstringDetector,
    'NewForGetclassDetector': NewForGetclassDetector,
    'IsAbsoluteFileNameDetector': IsAbsoluteFileNameDetector,
    'UselessControlFlowNextLineDetector': UselessControlFlowNextLineDetector,
    'NextIntViaNextDoubleDetector': NextIntViaNextDoubleDetector,
    'InefficientIndexOfDetector': InefficientIndexOfDetector,
    'DontJustCheckReadlineDetector': DontJustCheckReadlineDetector,
    'BoxingImmediatelyUnboxedDetector': BoxingImmediatelyUnboxedDetector,
    'ImmediateDereferenceOfReadlineDetector': ImmediateDereferenceOfReadlineDetector,
}