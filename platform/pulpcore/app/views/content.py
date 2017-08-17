import os

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, StreamingHttpResponse
from django.views.generic import View

from wsgiref.util import FileWrapper

from pulpcore.app.models import Distribution


class ContentView(View):
    """
    Content endpoint.

    URL matching algorithm.

    http://redhat.com/cdn/stage/files/manifest
                     |--------------||--------|
                            (1)          (2)

    1. Match: Distribution.base_path
    2. Match: PublishedFile.relative_path
    """

    BASE_URL = '/content'

    @staticmethod
    def _base_paths(path):
        """
        Get a list of base paths used to match a distribution.

        Args:
            path (str): The path component of the URL.

        Returns:
            list: Of base paths.

        """
        tree = []
        while True:
            base, _ = os.path.split(path)
            if not base:
                break
            tree.append(base.lstrip('/'))
            path = base
        return tree

    def _match(self, path):
        """
        Match either a PublishedArtifact or PublishedMetadata.

        Args:
            path (str): The path component of the URL.

        Returns:
            str: The storage path of the matched object.

        Raises:
            ObjectDoesNotExist: The referenced object does not exist.
            None: When not matched.

        """
        base_paths = self._base_paths(path)
        distribution = Distribution.objects.get(base_path__in=base_paths)
        publication = distribution.publication
        rel_path = path.lstrip(distribution.base_path)
        # artifact
        try:
            pa = publication.published_artifact.get(relative_path=rel_path)
        except ObjectDoesNotExist:
            pass
        else:
            artifact = pa.content_artifact.artifact
            if artifact.file:
                return artifact.file.name
            else:
                return None
        # metadata
        pm = publication.published_metadata.get(relative_path=rel_path)
        if pm.file:
            return pm.file.name
        else:
            return None

    @staticmethod
    def _stream(storage_path):
        """
        Get streaming response.

        Args:
            storage_path (str): The storage path of the requested object.

        Returns:
            HttpResponse: Always.

        """
        try:
            file = FileWrapper(open(storage_path, 'rb'))
        except FileNotFoundError:
            return HttpResponseNotFound()
        response = StreamingHttpResponse(file)
        response['Content-Length'] = os.path.getsize(storage_path)
        response['Content-Disposition'] = \
            'attachment; filename={n}'.format(n=os.path.basename(storage_path))
        return response

    @staticmethod
    def _redirect(storage_path):
        """
        Redirect to streamer.

        Args:
            storage_path (str): The storage path of the requested object.

        Returns:

        """
        # :TODO:

    @staticmethod
    def _xsend(storage_path):
        """
        Stream using X-SEND.

        Args:
            storage_path (str): The storage path of the requested object.

        Returns:

        """
        # :TODO:

    def get(self, request):
        """
        Get content artifact (bits).

        Args:
            request (django.http.HttpRequest): A request for a content artifact.

        Returns:
            django.http.StreamingHttpResponse: on found.
            django.http.HttpResponseNotFound: on not-found.

        """
        try:
            storage_path = self._match(request.path.lstrip(self.BASE_URL))
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        # TODO: Eventually, choose _redirect() and _xsend() as appropriate.
        return self._stream(storage_path)
