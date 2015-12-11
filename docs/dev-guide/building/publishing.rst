Publishing the Build
--------------------

Alpha builds should only be published to the testing repository. If you have a beta or stable build
that has passed tests in the testing repository, and you wish to promote it to the appropriate
place, you can use a similar rsync command to do so::

    $ rsync -avz --delete * pulpadmin@repos.fedorapeople.org:/srv/repos/pulp/pulp/<stream>/<X.Y>/ --dry-run

Replace stream with "beta" or "stable", and substitute the correct version. For our 2.4 beta
example::

    $ rsync -avz --delete * pulpadmin@repos.fedorapeople.org:/srv/repos/pulp/pulp/beta/2.4/ --dry-run

Note the ``--dry-run`` argument. This causes rsync to print out what it *would* do. Review its
output to ensure that it is correct. If it is, run the command again while omitting that flag.

.. warning::

   Be sure to check that you are publishing the build to the correct repository. It's important to
   never publish an alpha build to anything other than a testing repository. A beta build can go to
   testing or the beta repository (but never the stable repository), and a stable build can go to a
   testing or a stable repository.

If you have published a beta build, you must move all issues and stories for the target release
from ``MODIFIED`` to ``ON_QA``.

After publishing a beta build, email pulp-list@redhat.com to announce the beta. Here is a
typical email you can use::

   Subject: [devel] Pulp beta <version> is available

   Pulp <version> has been published to the beta repositories[0]. This fixes <add some text here>.

   [0] https://repos.fedorapeople.org/repos/pulp/pulp/beta/

If you have published a stable build, there are a few more items to take care of:

#. Update the "latest release" text on http://www.pulpproject.org/.
#. Contact Brian or Michael to update the documentation builders to use the new tag.
#. Update the channel topic in #pulp on Freenode with the new release.
#. Move all bugs that were in the ``MODIFIED``, ``ON_QA``, or ``VERIFIED`` state for this target
   release to ``CLOSED CURRENTRELEASE``.

After publishing a stable build, email pulp-list@redhat.com to announce the new release. Here is
a typical email you can use::

   Subject: Pulp <version> is available!

   The Pulp team is pleased to announce that we have released <version>
   to our stable repositories[0]. <Say if it's just bugfixes or bugs and features>.

   Please see the release notes[1][2][3] if you are interested in reading about
   the fixes that are included. Happy upgrading!

   [0] https://repos.fedorapeople.org/repos/pulp/pulp/stable/<stream>/
   [0] link to pulp release notes (if updated)
   [0] link to pulp-rpm release notes (if updated)
   [0] link to pulp-puppet release notes (if updated)

Please ensure that the release notes have in fact been updated before sending the email out.
