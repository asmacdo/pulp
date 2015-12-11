Submit to Koji
^^^^^^^^^^^^^^

We are now prepared to submit the build to Koji. This task is simple::

    $ cd pulp_packaging/ci
    $ ./build-all.py 2.6-testing --release

This command will build SRPMs, upload them to Koji, and monitor the resulting builds. If any of them
fail, you can view the
`failed builds <http://koji.katello.org/koji/tasks?state=failed&view=tree&method=all&order=-id>`_ to
see what went wrong. If the build was successful, it will automatically download the results into a
new folder called mash that will be a peer to the ``pulp_packaging`` directory.

At the end it will automatically upload the resulting build to fedorapeople in the directory
specified in the release config file. You can disable the push to fedorapeople by supplying
--disable-push flag.

If you want to start our Jenkins builder to run the unit tests in all the supported operating
systems, you should wait until the build script is finished so that it can push the correct tag to
GitHub. You can configure Jenkins to run the tests in the git branch or tag that you are building.
Make sure these pass before publishing the build.

