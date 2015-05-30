#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/utsname.h>

/*
 * argv0switch - a very simple program to exec other programs based on
 * the architecture. This comes from the need to have both 32- and 64-bit
 * binaries present on the system, but where the current location and names
 * of such executables can not be changed, for whatever reason. As a trivial
 * example, we want /usr/bin/gdb to always be gdb, but we want it to invoke
 * gdb32 if the platform is 32-bit, or gdb64 if the platform is 64-bit.
 *
 * The program is intentionally very very dumb. All it does is append the
 * text "32" or "64" to whatever argv[0] is, and exec's that. Thus, you would
 * only use this in real cases where you have 32 and 64 bit versions of a
 * binary. If the path in argv[0] is absolute or explicitly relative, then
 * this uses execv(). If it is neither, it uses execvp.
 */

int
main (int argc, char *argv[])
{
  struct utsname sys_uname;
  char *newprog;
  const char *suffix = 0;

  if (-1 == uname (&sys_uname)) {
    perror ("uname");
    exit (255);
  }

  /* Leave space for the 32 or 64, plus the NULL */
  newprog = malloc (strlen (argv[0]) + 3);
  strcpy (newprog, argv[0]);

  /*
   * ASSUMPTION: If the architecture contains the string 64, then we want
   * to run the 64-bit version of the program. If ever a 32-bit platform
   * is invented that has the string "64" in its architecture, this will
   * break.
   */
  suffix = "32";
  if ((char *)0 != strstr (sys_uname.machine, "64"))
    suffix = "64";

  strcat (newprog, suffix);

  /*
   * If any part of argv[0] contains a '/' character, it means the invocation
   * was absolute or explicitly relative. That is, it is not being exec'ed
   * via the PATH. In such cases, we don't exec via the PATH either. If no
   * such character exists there, then we exec via the PATH.
   */
  if ((char *)0 == strchr (newprog, '/')) {
    return execvp (newprog, argv);
  } else {
    return execv (newprog, argv);
  }
}
