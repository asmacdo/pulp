Release Build
^^^^^^^^^^^^^

Before you begin a release build, make sure that the appropriate release notes exist. 

0. Update the build config yaml file. 
   :ref` </dev-guide/building/build-concepts/build>

   Specifically, make sure that the `git-branch` field for each of the packages you are building points to the tag created when building the release candidate. This should follow the format `<package_name>-<previous_version>.rc`. For all branches you are not building, make sure that the `git-branch` field points to a release branch rather than a previous tag.

  The `version` field should be be `X.Y.Z-1` for all packages being built, and should not change for packages that do not need to be built.

0. Use `ssh-add` to allow the current session to rsync to the appropriate repo.

0. Build it!  # TODO (asmacdo) link to "Submit to koji"
   :ref` </dev-guide/building/build-concepts/using-koji>

0. Merge changes forward TODO asmacdo get link

0. Sign them! 

0. Publish it!!!


New Stable Major/Minor Versions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are publishing a new stable <X.Y> build that hasn't been published before (i.e., X.Y.0-1),
you must also update the symlinks in the repository. There is no automated tool to perform this
step. ssh into repos.fedorapeople.org using the SSH keypair, and perform the task manually. Ensure
that the "X" symlink points at the latest X.Y release, and ensure that the "latest" symlink points
at that largest "X" symlink. For example, if you just published 3.1.0, and the latest 2.Y version
was 2.5, the stable folder should look similar to this::

    [pulpadmin@people03 pulp]$ ls -lah stable/
    total 24K
    drwxrwxr-x. 6 pulpadmin pulpadmin 4.0K Sep 17 18:26 .
    drwxrwxr-x. 7 jdob      gitpulp   4.0K Sep  8 22:40 ..
    lrwxrwxrwx. 1 pulpadmin pulpadmin    3 Aug  9 06:35 2 -> 2.5
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Aug 15  2013 2.1
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Sep  6  2013 2.2
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Dec  5  2013 2.3
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Aug  9 06:32 2.4
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Aug 19 06:32 2.5
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Aug 20 06:32 3.0
    drwxrwxr-x. 7 pulpadmin pulpadmin 4.0K Aug 24 06:32 3.1
    lrwxrwxrwx. 1 pulpadmin pulpadmin    3 Aug 24 06:35 3 -> 3.1
    lrwxrwxrwx. 1 pulpadmin pulpadmin   29 Aug 20 06:32 latest -> /srv/repos/pulp/pulp/stable/3

The ``rhel-pulp.repo`` and ``fedora-pulp.repo`` files also need to be updated
for the new GPG public key location if you are creating a new X release.
