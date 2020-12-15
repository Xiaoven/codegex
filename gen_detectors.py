from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.dumb_methods import StringCtorDetector, RandomD2IDetector, RandomOnceDetector, \
    FinalizerOnExitDetector
from patterns.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from patterns.detect.find_ref_comparison import EqualityDetector, CalToNullDetector
from patterns.detect.find_rough_constants import FindRoughConstantsDetector
from patterns.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
from patterns.detect.format_string_checker import NewLineDetector
from patterns.detect.incompat_mask import IncompatMaskDetector
from patterns.detect.infinite_recursive_loop import CollectionAddItselfDetector
from patterns.detect.inheritance_unsafe_get_resource import GetResourceDetector
from patterns.detect.method_return_check import NotThrowDetector
from patterns.detect.naming import SimpleNameDetector2, SimpleNameDetector1
from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod
from patterns.detect.static_calendar_detector import StaticDateFormatDetector

DETECTORS = [IncompatMaskDetector(), GetResourceDetector(), StaticDateFormatDetector(), NotThrowDetector(),
             CollectionAddItselfDetector(), FindRoughConstantsDetector(), EqualityDetector(), CalToNullDetector(),
             SimpleNameDetector1(), SimpleNameDetector2(), DontCatchIllegalMonitorStateException(),
             ExplicitInvDetector(), PublicAccessDetector(), DefSerialVersionID(), DefReadResolveMethod(),
             SuspiciousCollectionMethodDetector(), FinalizerOnExitDetector(), RandomOnceDetector(), RandomD2IDetector(),
             StringCtorDetector(), NewLineDetector()]
