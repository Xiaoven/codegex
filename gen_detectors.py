from patterns.detect.incompat_mask import IncompatMaskDetector
from patterns.detect.inheritance_unsafe_get_resource import GetResourceDetector
from patterns.detect.static_calendar_detector import StaticDateFormatDetector
from patterns.detect.method_return_check import NotThrowDetector
from patterns.detect.overriding_equals_not_symmetrical import EqualsClassNameDetector
from patterns.detect.infinite_recursive_loop import CollectionAddItselfDetector
from patterns.detect.find_rough_constants import FindRoughConstantsDetector
from patterns.detect.find_ref_comparison import EqualityDetector, CallToNullDetector
from patterns.detect.naming import SimpleNameDetector1, SimpleNameDetector2
from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod, DefMethodPrivate
from patterns.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from patterns.detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, \
    StringCtorDetector, InvalidMinMaxDetector
from patterns.detect.format_string_checker import NewLineDetector

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
    "SimpleNameDetector1": SimpleNameDetector1,
    "SimpleNameDetector2": SimpleNameDetector2,
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
    "DefMethodPrivate": DefMethodPrivate
}