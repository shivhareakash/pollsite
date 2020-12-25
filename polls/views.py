from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from .models import Question, Choice
from django.views import generic

from django.urls import reverse
from django.utils import timezone

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:15]
#     # output = '<br>'.join([q.question_text for q in latest_question_list])
#     # return HttpResponse("Here is the list of the latest questions:<br>"+output)
#     context = {'latest_question_list':latest_question_list}
#     return render(request, 'index.html', context)

# def detail(request, question_id):
#     # return HttpResponse("Here is the detail of the Question %s" % question_id)
    
#     # With Http404 exception
#     question_detail=get_object_or_404(Question, pk=question_id)


#     # Without Http exception
#     # question_detail = Question.objects.get(pk=question_id)


#     # This is an alternative method
#     # options = Choice.objects.filter(q__id=(question_id)) 
#     # context = {question_detail:options}
#     # return render(request,"detail.html", {'context':context})

#     return render(request,"detail.html", {'context':question_detail})
    
# def results(request, question_id):
#     # return HttpResponse("Here is the result of the Question %s" % question_id)
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "results.html", {"question":question})


## Using Generic view
class Index(generic.ListView):
    template_name = "index.html"
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """exclude questions without choice and future date"""
        published_question_with_choices = Question.objects.filter(choice__isnull=False).filter(pub_date__lte=timezone.now()).order_by('-pub_date').distinct()[:50] 
        #Filtering on m2m relationships will return the origin model multiple times if there are multiple related objects that fulfil the filter. You should add distinct() to your query. 
        #Since there are 3 choices, same question will be shown thrice without distinct()
        
        return published_question_with_choices #- indicates ascending order here
       
    # def get_queryset(self):
    #     """
    #     Excludes any questions that aren't published yet.
    #     """
    #     return Question.objects.filter(pub_date__lte=timezone.now())

class Detail(generic.DetailView):
    model = Question
    template_name = "detail.html"
    context_object_name='context'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_question_with_choices = Question.objects.filter(choice__isnull=False).filter(pub_date__lte=timezone.now()).distinct()
        return published_question_with_choices

class Results(generic.DetailView):
    model = Question
    template_name = "results.html"

    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet and have no choice
        """
        # return Question.objects.filter(pub_date__lte=timezone.now())

        published_question_with_choices = Question.objects.filter(choice__isnull=False).filter(pub_date__lte=timezone.now()).distinct()
        return published_question_with_choices

def vote(request, question_id):
    # return HttpResponse("Please cast your vote for the Question%s" % question_id)

    # question = get_object_or_404(Question, pk=question_id)
    
    # #  here instead of Question model, we can also pass filtered question query
    queryset=Question.objects.filter(choice__isnull=False).distinct()
    question = get_object_or_404(queryset, pk=question_id)
    
    
   
    try:
        choice_key = request.POST['choice']
        selected_choice = question.choice_set.get(pk=choice_key)

    except(KeyError, Choice.DoesNotExist):
        #Redsplay the question voting form.
        return render(request, 'detail.html', {
            'context':question,
             "error_message":"You didnt' select a choice"})
    else:
        selected_choice.votes += 1
        selected_choice.save()
# Always return an HttpResponseRedirect after successfully dealing
# with POST data. This prevents data from being posted twice if a
# user hits the Back button.

## Both these return do the same work, the reverse method loads the result url http://127.0.0.1:8000/polls/3/results/, whereas the render method renders the results.html on the same page. http://127.0.0.1:8000/polls/3/vote/
        
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,))) 
        # # Since we are calling results url here, it needs an argument for the url.


        # return render(request, 'results.html', {'question':question})  
        #In this case, we are not even calling result view so no args needed, we are directly rendering results.html from here


