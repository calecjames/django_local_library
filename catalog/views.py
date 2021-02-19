from django.shortcuts import render

from django.views import generic
# Create your views here.

from catalog.models import Book, Author, BookInstance, Genre

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.decorators import login_required, permission_required

import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception = True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance,pk=pk)

    #If this is a post request then process the form data

    if request.method == "POST":

        #Create a form instance and populate it with the data from the request (binding)
        form = RenewBookForm(request.POST)

        #Check if the form is valid:

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            #Redirect to a new url
            return HttpResponseRedirect(reverse("all-borrowed"))

    #If this is a GET or any other method create the default form.

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html',context)

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view as counted in the session variable.
    num_visits = request.session.get('num_visits',1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits':num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'   # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='the')[:2] # Get 5 books containing the title war
    template_name = 'books/my_arbitrary_template_name_list.html'
    paginate_by = 1

    '''def get_queryset(self):
        return Book.objects.filter(title__icontains = 'Wise')[:5]

    def get_context_data(self, **kwargs):
        #Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        #Create any data and add it to the context
        context['some__data'] = 'this is just some data'
        return context

    context_object_name = 'book_list'
    template_name = 'books/my_arbitrary_template_name_list.html'
    '''

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'   # your own name for the list as a template variable
    #queryset = Author.objects.filter(first_name__icontains='Pat')[:2] # Get 5 books containing the title war
    template_name = 'books/my_arbitrary_template_name_list.html'
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


    # Or multiple permissions

    # Note that 'catalog.can_edit' is just an example
    # the catalog application doesn't have such permission!


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author, Book

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = ['title','author','summary','isbn','genre','language']

class BookUpdate(UpdateView):
    model = Book
    fields ="__all__"

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')