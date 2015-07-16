function loadPosts(posts_type, page){
  $('#loader').show();
  $('#posts_wrapper').load('/loadposts/'+posts_type+'/'+page, function(){
    $('.timestamp').trigger('load');
    $('#posts_wrapper').masonry({columnWidth: 266, itemSelector: '.post_container'});
    $('#loader').hide();
  });
}
