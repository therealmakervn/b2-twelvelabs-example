import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectTemplateResponseMixin, SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from cattube.settings import TWELVE_LABS_CLIENT, TWELVE_LABS_INDEX_ID, POLL_TRANSLOADIT, TRANSCRIPTS_PATH, TEXT_PATH, \
    LOGOS_PATH
from .forms import ResultForm
from .models import Video, SearchResult, add_new_files
from .tasks import poll_video_loading
from .utils import load_json_into_context, create_signed_transloadit_options

PAGE_SIZE = 12


class VideoListView(ListView):
    model = Video
    paginate_by = PAGE_SIZE
    ordering = ['-uploaded_at']

    def get_queryset(self):
        """
        Override default, so we can update the database with any new files in B2.
        """
        add_new_files(self.request.user)
        return super().get_queryset()


class VideoSearchView(ListView):
    model = Video
    paginate_by = PAGE_SIZE
    template_name = "core/video_results.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        
        if not query:
            return []
        
        print("\n=== DEBUG INFO ===")
        print(f"Query: {query}")
        
        try:
            videos = Video.objects.filter(status='Ready')
            print(f"Videos in DB: {videos.count()}")
            for v in videos:
                print(f"- {v.title} (ID: {v.id}, Status: {v.status})")
            
            options = {
                "index_id": TWELVE_LABS_INDEX_ID,
                "tasks": ["visual", "conversation", "text_in_video", "logo"],
                "group_by": "video"
            }
            
            print(f"\nTwelve Labs Config:")
            print(f"Index ID: {TWELVE_LABS_INDEX_ID}")
            print(f"API Key: {TWELVE_LABS_CLIENT.api_key[:5]}...")
            print(f"Options: {options}")
            
            results = TWELVE_LABS_CLIENT.search.query(
                query=query,
                options=options
            )
            
            print(f"\nSearch Results:")
            print(f"Raw response: {results}")
            print("=== END DEBUG ===\n")
            
            search_results = []
            for result in results.data:
                try:
                    video = videos.get(video_id=result.id)
                    search_results.append(SearchResult(
                        video=video,
                        clips=result.clips,
                        clip_count=len(result.clips)
                    ))
                except Video.DoesNotExist:
                    print(f"Video not found: {result.id}")
            
            return search_results
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get("q", "")
        return context


class VideoResultView(SingleObjectTemplateResponseMixin, SingleObjectMixin, View):
    """
    Drill down into a single search result. Parameters are POSTed to this page, since
    they include the search results for this video.
    """
    model = Video
    template_name = "core/video_result.html"
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        """
        Get the object from the "id" form parameter, referenced here as "pk"
        """
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(pk=self.pk)

    # noinspection PyAttributeOutsideInit
    def post(self, request):
        """
        Handle the POST, using a Form to extract the parameters, and populate the context with the search
        results (clips), query, and all the video data.
        """
        form = ResultForm(request.POST)
        if not form.is_valid():
            raise ValidationError("Invalid form", code="invalid")

        self.pk = form.cleaned_data['id']
        self.object = self.get_object()

        context = self.get_context_data(object=self.object)
        context['clips'] = json.loads(form.cleaned_data['clips'])
        context['query'] = form.cleaned_data['query']
        load_json_into_context(context, [TRANSCRIPTS_PATH, TEXT_PATH, LOGOS_PATH], self.object)

        return render(request, self.template_name, context)


class VideoDetailView(DetailView):
    model = Video
    slug_field = 'id'
    slug_url_kwarg = 'video_id'

    def get_context_data(self, **kwargs):
        """
        Load all the video data from B2 into the context
        """
        context = super().get_context_data(**kwargs)
        load_json_into_context(context, [TRANSCRIPTS_PATH, TEXT_PATH, LOGOS_PATH], self.object)
        return context


@method_decorator(login_required, name='dispatch')
class VideoCreateView(CreateView):
    model = Video
    fields = ['title', 'assembly_id']

    def get_success_url(self):
        """
        Go to video detail page on success
        """
        return reverse_lazy('watch', kwargs={'video_id': self.object.id})

    def get_context_data(self, **kwargs):
        """
        Add the TransloadIt params and signature to the context
        """
        context = super().get_context_data(**kwargs)
        notify_url = None if POLL_TRANSLOADIT else self.request.build_absolute_uri(reverse('notification'))
        context.update(create_signed_transloadit_options(notify_url))
        return context

    # noinspection PyAttributeOutsideInit
    def form_valid(self, form):
        form.instance.user = self.request.user
        # Save the new object to the database before kicking off the polling task to avoid race conditions
        response = super().form_valid(form)
        if POLL_TRANSLOADIT:
            poll_video_loading(form.data['assembly_id'])
        return response


@method_decorator(login_required, name='dispatch')
class VideoDeleteView(DeleteView):
    model = Video
    slug_field = 'id'
    slug_url_kwarg = 'video_id'

    def form_valid(self, form):
        """
        Delete the file from B2 as well as the object from the database
        """
        video_name = self.get_object().video.name
        print(f'Deleting: {video_name}')
        default_storage.delete(video_name)
        print(f'Deleted: {video_name}')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')
