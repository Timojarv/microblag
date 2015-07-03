function loadPosts(posts_type){
  $('#loader').show();
  $('#posts_wrapper').load('/loadposts/'+posts_type+'/1', function(){
    $('#loader').hide();
    });
}
