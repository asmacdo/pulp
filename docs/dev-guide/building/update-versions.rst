Updating Versions
^^^^^^^^^^^^^^^^^

We use Jenkins to make nightly builds, so once you have built the package successfully and merged the
changelog forward, you should update the yaml file that Jenkins uses and bump the versions of all the
projects that were included in this build. Most likely it is the same file you were using to build
the packages in the previous step. You can use ``update-version-and-merge-forward.py`` to update
the versions. This script checks out all the projects and updates the version in the spec file and
in all of the setup.py files.

At this point you can inspect the files to ensure the versions are as you expect. You can rerun the
script with ``--push`` flag to push the changes to Github.

You should also push the changes in the yaml file inside of pulp_packaging to Github.


Merging Tags Forward
^^^^^^^^^^^^^^^^^^^^

After the repositories are built, the next step is to merge the tag changes you have made all the
way forward to master.

.. warning::

   Do not use the ours strategy, as that will drop the changelog entries. You must manually resolve
   the conflicts!

You will experience conflicts with this step if you are building a stream that is not the latest stream.
Be sure to merge forward on all of the repositories, keeping the changelog entries in chronological
order. Be cautious not to clobber the versions in the spec file! Then you can ``git push <branch>:<branch>``
after you check the diff to make sure it is correct. Lastly, do a new git checkout elsewhere and check that
``tito build --srpm`` is tagged correctly and builds.


