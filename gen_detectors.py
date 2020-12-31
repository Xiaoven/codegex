from patterns.detect.inheritance_unsafe_get_resource import GetResourceDetector
from patterns.detect.incompat_mask import IncompatMaskDetector
from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod
from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.find_rough_constants import FindRoughConstantsDetector
from patterns.detect.naming import SimpleNameDetector1, SimpleNameDetector2
from patterns.detect.method_return_check import NotThrowDetector
from patterns.detect.format_string_checker import NewLineDetector
from patterns.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from patterns.detect.find_ref_comparison import EqualityDetector, CalToNullDetector
from patterns.detect.static_calendar_detector import StaticDateFormatDetector
from patterns.detect.infinite_recursive_loop import CollectionAddItselfDetector
from patterns.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from patterns.detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, StringCtorDetector

DETECTOR_DICT = {
    "GetResourceDetector": GetResourceDetector,
    "IncompatMaskDetector": IncompatMaskDetector,
    "DefSerialVersionID": DefSerialVersionID,
    "DefReadResolveMethod": DefReadResolveMethod,
    "DontCatchIllegalMonitorStateException": DontCatchIllegalMonitorStateException,
    "FindRoughConstantsDetector": FindRoughConstantsDetector,
    "SimpleNameDetector1": SimpleNameDetector1,
    "SimpleNameDetector2": SimpleNameDetector2,
    "NotThrowDetector": NotThrowDetector,
    "NewLineDetector": NewLineDetector,
    "ExplicitInvDetector": ExplicitInvDetector,
    "PublicAccessDetector": PublicAccessDetector,
    "EqualityDetector": EqualityDetector,
    "CalToNullDetector": CalToNullDetector,
    "StaticDateFormatDetector": StaticDateFormatDetector,
    "CollectionAddItselfDetector": CollectionAddItselfDetector,
    "SuspiciousCollectionMethodDetector": SuspiciousCollectionMethodDetector,
    "FinalizerOnExitDetector": FinalizerOnExitDetector,
    "RandomOnceDetector": RandomOnceDetector,
    "RandomD2IDetector": RandomD2IDetector,
    "StringCtorDetector": StringCtorDetector
}