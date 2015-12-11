Updating Docs
-------------

When releasing a new X or Y release, the internal links in the docs need to be updated to match.

The docs for Pulp platform and each plugin use `intersphinx <http://sphinx-doc.org/ext/intersphinx.html>`_
to facilitiate linking between documents. It is important that each branch
of Pulp and Pulp plugins link to the correct versions of their sister
documents.  This is accomplished by editing the URLs in the
``intersphinx_mapping`` variable, which is set in ``docs/conf.py`` for
both Pulp platform and all plugins.

Here are some guidelines for what to set the URL to:
 - The master branch of Pulp or any plugins should always point to "latest".
 - Plugins should point to the latest stable version of Pulp that they are
   known to support.
 - Pulp platform's intersphinx URLs should point back to whatever the plugin is
   set to. For example, if the "pulp_foo" plugin's docs for version 1.0 point to
   the "2.8-release" version of the Pulp platform docs, then platform version
   2.8 should point back to "1.0-release" for pulp_foo's docs. This ensures a
   consistent experience when users click back and forth between docs.
