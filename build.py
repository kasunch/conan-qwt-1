from cpt.packager import ConanMultiPackager
from cpt_helpers.build_helper import *
import traceback

if __name__ == "__main__":
    try:
        builder = ConanMultiPackager(reference="%s/%s" % get_name_and_version(), out=hidesensitive)
        builder.add_common_builds(pure_c=False)
        builder.run()
    except Exception as e:
        hidesensitive(traceback.format_exc())
        hidesensitive(str(e))
        sys.exit(1)
