from detect.URL_problems import URLCollectionDetector
from detect.bad_syntax_for_regular_expression import SingleDotPatternDetector, FileSeparatorAsRegexpDetector
from detect.find_dead_local_stores import FindDeadLocalIncrementInReturn
from detect.find_puzzlers import BadMonthDetector, ShiftAddPriorityDetector, ReuseEntryInIteratorDetector, \
    MultiplyIRemResultDetector, AnonymousArrayToStringDetector
from detect.find_self_comparison import CheckForSelfComputation, CheckForSelfComparison
from detect.incompat_mask import IncompatMaskDetector
from detect.inheritance_unsafe_get_resource import GetResourceDetector
from detect.questionable_boolean_assignment import BooleanAssignmentDetector
from detect.static_calendar_detector import StaticDateFormatDetector
from detect.method_return_check import NotThrowDetector
from detect.overriding_equals_not_symmetrical import EqualsClassNameDetector
from detect.infinite_recursive_loop import CollectionAddItselfDetector
from detect.find_rough_constants import FindRoughConstantsDetector
from detect.find_ref_comparison import EqualityDetector, CallToNullDetector
from detect.naming import SimpleSuperclassNameDetector, SimpleInterfaceNameDetector, HashCodeNameDetector, \
    ToStringNameDetector, EqualNameDetector, ExceptionClassNameDetector
from detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod, DefPrivateMethod
from detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, \
    StringCtorDetector, InvalidMinMaxDetector, VacuousEasyMockCallDetector, BigDecimalConstructorDetector, \
    NonsensicalInvocationDetector, BooleanCtorDetector, NumberCTORDetector, FPNumberCTORDetector, \
    BoxedPrimitiveToStringDetector, BoxedPrimitiveForParsingDetector, BoxedPrimitiveForCompareDetector
from detect.format_string_checker import NewLineDetector
from detect.find_float_equality import FloatEqualityDetector
from detect.find_puzzlers import OverwrittenIncrementDetector
from detect.find_bad_cast import FindBadCastDetector
from detect.naming import ClassNameConventionDetector, MethodNameConventionDetector
from detect.dont_use_enum import DontUseEnumDetector
from detect.find_self_assignment import CheckForSelfAssignment, CheckForSelfDoubleAssignment
from detect.synchronize_on_class_literal_not_get_class import SynGetClassDetector
from detect.volatile_usage import VolatileArrayDetector
from detect.wait_in_loop import NotifyDetector
from detect.dumb_method_invocations import UselessSubstringDetector, IsAbsoluteFileNameDetector
from detect.dumb_methods import NewForGetclassDetector, NextIntViaNextDoubleDetector
from detect.find_useless_control_flow import UselessControlFlowNextLineDetector
from detect.inefficient_indexOf import InefficientIndexOfDetector
from detect.bad_use_of_return_value import DontJustCheckReadlineDetector
from detect.dumb_method_invocations import UselessSubstringDetector
from detect.find_puzzlers import BoxingImmediatelyUnboxedDetector
from detect.dumb_methods import ImmediateDereferenceOfReadlineDetector


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