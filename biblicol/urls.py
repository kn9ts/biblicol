from django.conf.urls import url
from . import views
from .controllers import search

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^search/(?P<param>[\w]+)/(?P<pageno>[0-9]{,3})$', search.index,
        name='search'),
]

# // Search path
# Route::get('search/{param?}/{pageno?}', array('as'=> 'search',
# 'uses'=> 'SearchController@index'));

# // Resource for reading the Bible
# Route::resource("read", "ReadingController");
# Route::resource("read.chapter", "ChaptersController");
# Route::resource("read.chapter.verse", "SearchController");

# // Expand on a single verse
# Route::resource("reference", "ReferenceController");

# // Create URL Friendly searches response
# Route::get('filter', array('as' => 'filter', 'uses' => function () {
#   $param = preg_replace('/(\s|\%20)/', '_', Input::get('param'));
#   return Redirect::to("/search/$param");
# }));

# Route::resource('subscribe', 'SubscribersController', array('except'=> array('delete')));
# Route::delete('unsubscribe', 'SubscribersController@destroy');

# // eg. http://localhost:8000/someone
# // Route::get('/{something}', function($something) {
# //  return Redirect::to("filter")->withInput(array('param' => $something));
# // });

# // Internal functions
# Route::get('/books/dump', array('as'=> 'books',
# 'uses' = > 'BooksController@storeBooksFromAPI'));
# Route::get('/books/getfrom/api', array('as'=> 'books',
# 'uses'=> 'BooksController@getBooksFromAPI'));

# Route::get('/hostname', function() {
#     return [gethostname(), App::environment()];
# });
