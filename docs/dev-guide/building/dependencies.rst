Building Dependencies
^^^^^^^^^^^^^^^^^^^^^

If you wish to add or update the version or release of one of our dependencies, you should begin by
adding/updating the dependency's tarball, patches, and spec file in the Pulp git repository as
appropriate for the task at hand. **Don't forget to set the version/release in the spec file.** Once
you have finished that work, you are ready to test the changes. In the directory that contains the
dependency, use tito to build a test RPM. For example, for python-celery::

    $ cd deps/python-celery
    $ tito build --test --rpm

Pay attention to the output from tito. There may be errors you will need to respond to. If all goes
well, it should tell you the location that it placed some RPMs. You should install these RPMs and
test them to make sure they work with Pulp and that you want to introduce this change to the
repository.

If you are confident in your changes, submit a pull request with the changes you have made so far.
Once someone approves the changes, merge the pull request. Once you have done this, you are ready to
tag the git repository with your changes::

    $ tito tag --keep-version

Pay attention to the output of tito here as well. It will instruct you to push your branch and the
new tag to GitHub.

.. warning::

   It is very important that you perform the steps that tito instructs you to do. If you do not,
   others will not be able to reproduce the changes you have made!

At this point the dependency will automatically be built during all test builds of Pulp and will
automatically have a release build performed when the next release build containing this
dependency is performed.


