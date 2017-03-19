from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^create_user/$', views.create_user, name='create_user'),
	url(r'^dynamic_form/$', views.dynamic_form_view, name='dynamic_form_view'),
	url(r'^recipes/$', views.recipes_view, name='recipes_view'),
	url(r'^recipes/(?P<pk>\d+)/$', views.recipe_details, name='recipe_details'),
	url(r'^history/$', views.history_view, name='history_view'),
	url(r'^history/(?P<pk>\d+)/$', views.history_details, name='history_details'),
	url(r'^save/(?P<servings>.*)/(?P<recipe>.*) $', views.save, name='save'),
	url(r'^ingredient_list/$', views.ingredient_list, name='ingredient_list'),
	url(r'^add_ingredient/(?P<pk>\d+)/$', views.add_specific_ingredient, name='add_specific_ingredient'),
	url(r'^add_ingredient/$', views.add_ingredient, name='add_ingredient'),
	# special views for populating the database
	url(r'^reset_database/$', views.reset_database, name='reset_database'),
]