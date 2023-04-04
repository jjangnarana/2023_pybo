from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count

from ..models import Question

def index(request):
    page = request.GET.get('page', '1') # 페이지
    kw = request.GET.get('kw', '') # 검색어
    question_list = Question.objects.order_by('-create_date')
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) | #제목 검색
            Q(content__icontains=kw) | #내용 검색
            Q(answer__content__icontains=kw) | #답변 내용 검색
            Q(author__username__icontains=kw) | #질문 작성자 검색
            Q(answer__author__username__icontains=kw) #답변 작성자 검색
        ).distinct()
    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)
    current_page = page_obj.number
    start_index = (current_page - 1) // 10 * 10
    end_index = start_index + 10
    page_range = paginator.page_range[start_index:end_index]
    context = {
        'question_list' : page_obj,
        'page_range' : page_range,
        'page' : page,
        'kw' : kw,
    }
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    page = request.GET.get('page', '1')
    vote_sort = request.GET.get('vote_sort', '')
    print(request.GET)
    question = get_object_or_404(Question, pk=question_id)
    if vote_sort == 'votes_desc':
        answer_list = question.answer_set.annotate(voter_count=Count('voter')).order_by('-voter_count')
    elif vote_sort == 'votes_asc':
        answer_list = question.answer_set.annotate(voter_count=Count('voter')).order_by('voter_count')
    else:
        answer_list = question.answer_set.all().order_by('-create_date')
    
    paginator = Paginator(answer_list, 5)
    try:
        answers = paginator.page(page)
    except PageNotAnInteger:
        answers = paginator.page(1)
    except EmptyPage:
        answers = paginator.page(paginator.num_pages)
    current_page = answers.number
    start_index = (current_page - 1) // 10 * 5
    end_index = start_index + 5
    page_range = paginator.page_range[start_index:end_index]
    context = {'question': question, 
               'answers' : answers,
               'page_range' : page_range,
               'page' : page,
               'vote_sort' : vote_sort
               }
    return render(request, 'pybo/question_detail.html', context)