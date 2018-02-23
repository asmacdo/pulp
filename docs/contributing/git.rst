Git
===

TODO(from PUP3) We do Git Github. Link to "a successful branching strategy" or whatever. Link to
git org page. This document is definitive for pulpcore only, but some plugins may choose to follow
the same strategies.

.. _git-branch:

Branches
--------

.. note::

    During development of Pulp 3.0, we will be using the `3.0-dev` branch instead of `master`.

Commits
-------

TODO(1 per change)

Squash
******

Commit Messages
***************

Commit messages in Pulp should contain a human readable explanation of what
was fixed in the commit. They should also follow the standard git message
format of starting with a subject line or title (usually wrapped at about 50
chars) and optionally, a longer message (usually wrapped at 72 characters)
broken up into paragraphs. For more on what constitutes a good commit message,
we recommend `Tim Pope's blog post on the subject
<http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.

It's also recommended that every commit message in Pulp reference an issue in
`Pulp's Redmine issue tracker <https://pulp.plan.io>`_. To do this you should
use both a keyword and a link to the issue.

To reference the issue (but not change its state), use ``re`` or ``ref``::

    re #123
    ref #123

To update the issue's state to MODIFIED and set the %done to 100, use
``fixes`` or ``closes``::

    fixes #123
    closes #123

You can also reference multiple issues in a commit::

    fixes #123, #124

Putting this altogether, the following is an example of a good commit message::

    Update node install and quickstart

    The nodes install and quickstart was leaving out an important step on
    the child node to configure the server.conf on the child node.

    closes #1392
    https://pulp.plan.io/issues/1392
