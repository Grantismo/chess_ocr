AM_CFLAGS = -Wall -march=native -pipe
AM_LDFLAGS = -lm

if DEBUG
AM_CFLAGS += -O0 -ggdb
else
AM_CFLAGS += -O3
AM_LDFLAGS += -s
endif

AM_CXXFLAGS = $(AM_CFLAGS)

bin_PROGRAMS = chess

chess_SOURCES = chess.c chess_features.c corner_detect.c feature_orientation.c gaussian_blur5.c non_max_sup_pts.c pgm.c

CONFIG_HASH := $(shell sha1sum config.status | cut -c-40)
GIT_UNCLEAN := $(shell cd "$(abs_top_srcdir)" && [ "`git status --porcelain -uno`" ] && echo -n "un"; echo "clean" )
GIT_REVISION := $(shell cd "$(abs_top_srcdir)" && git rev-list --max-count=1 HEAD)-$(GIT_UNCLEAN)
AM_CFLAGS += -DGIT_REVISION=$(GIT_REVISION)

-include TRACKER-CONFIG-HASH
-include TRACKER-VERSION-FILE

TRACKER-CONFIG-HASH: FORCE
@GMAKE_IFNEQ@ ($(CONF_HASH),$(CONFIG_HASH))
	$(shell echo "CONF_HASH = $(CONFIG_HASH)" > TRACKER-CONFIG-HASH)
@GMAKE_ENDIF@
@GMAKE_INCLUDE@ TRACKER-CONFIG-HASH

TRACKER-VERSION-FILE: FORCE
@GMAKE_IFNEQ@ ($(GIT_REV),$(GIT_REVISION))
	$(shell echo "GIT_REV = $(GIT_REVISION)" > TRACKER-VERSION-FILE)
@GMAKE_ENDIF@
@GMAKE_INCLUDE@ TRACKER-VERSION-FILE

*.o: TRACKER-CONFIG-HASH TRACKER-VERSION-FILE

all-local:
	@if test "$(GIT_UNCLEAN)" = "unclean"; then						\
		echo "************************************************************************";\
		echo "";									\
		echo "UNCOMMITED CHANGES -- Git revision in output will be inaccurate";		\
		echo "";									\
		echo "************************************************************************";\
	fi

treeclean: maintainer-clean
	rm -f aclocal.m4 config.guess config.h.in config.h.in~ config.sub configure depcomp install-sh Makefile.in missing

clean-local:
	rm -f TRACKER-CONFIG-HASH TRACKER-VERSION-FILE

.PHONY: FORCE
