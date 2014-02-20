# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.60])
AC_INIT([ChESS], [1.0], [sb476@cam.ac.uk])
AM_INIT_AUTOMAKE([1.11 foreign no-dist -Wall -Wno-portability -Werror])
AC_CONFIG_SRCDIR([chess.c])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile])

AM_SILENT_RULES([yes])

AC_SUBST(GMAKE_IFNEQ, [ifneq])
AC_SUBST(GMAKE_ENDIF, [endif])
AC_SUBST(GMAKE_INCLUDE, [include])

# Checks for programs.
# save $CFLAGS since AC_PROG_CC likes to insert "-g -O2"
ac_save_CFLAGS="$CFLAGS"
AC_PROG_CC
CFLAGS="$ac_save_CFLAGS"
AC_PROG_CC_C99
AC_PROG_CXX

# Checks for libraries.

# Use optimization (default) or debug CFLAGS
AC_ARG_ENABLE(debug, [AC_HELP_STRING([--enable-debug], [Turn on debugging (default=disabled)])],
	      [enable_debug="$enableval"], [enable_debug=no])
AM_CONDITIONAL(DEBUG, [test "x${enable_debug}" = "xyes"])
if test "x${enable_debug}" = "xyes"; then
	build_type="debug"
else
	build_type="optimized"
fi

# Checks for header files.
AC_CHECK_HEADERS([stddef.h stdint.h stdlib.h string.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_HEADER_STDBOOL
AC_C_INLINE
AC_TYPE_INT16_T
AC_TYPE_OFF_T
AC_TYPE_SIZE_T
AC_TYPE_UINT16_T
AC_TYPE_UINT32_T
AC_TYPE_UINT64_T
AC_TYPE_UINT8_T

# Check whether SSE4.1 compiles and runs
AC_MSG_CHECKING([for SSE4.1 support (PMOVZXBW)])
ac_save_CFLAGS="$CFLAGS"
CFLAGS="$CFLAGS -march=native -msse4.1"
AC_RUN_IFELSE([AC_LANG_PROGRAM([#include <stdint.h>
				typedef char v16qi __attribute__ ((vector_size(16)));
				typedef int16_t v8hi __attribute__ ((vector_size(16)));],
			       [v16qi v16; v8hi v8; v8 = __builtin_ia32_pmovzxbw128(v16);])],
	      [have_pmovzxbw=yes], [have_pmovzxbw=no])
CFLAGS="$ac_save_CFLAGS"
if test "x${have_pmovzxbw}" = "xyes"; then
	AC_DEFINE(HAVE_PMOVZXBW, 1, [Define to 1 if SSE4.1 byte expansion assembly should be used])
else
	AC_DEFINE(HAVE_PMOVZXBW, 0, [Define to 1 if SSE4.1 byte expansion assembly should be used])
fi
AC_MSG_RESULT([$have_pmovzxbw])

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([memset])

AC_OUTPUT

echo
echo "------------------------------------------------------------------------"
echo
echo "Configuration Summary:"
echo
echo "  Use SSE4.1......................: $have_pmovzxbw"
echo
echo "  Build type......................: $build_type"
echo
