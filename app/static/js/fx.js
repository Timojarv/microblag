function redBox(object){
  oldColor = object.style.borderColor;
  object.style.borderColor='rgb(231, 76, 60)';
  object.oninput=function(){object.style.borderColor=oldColor};
}

function randomBG(){
  var delay = Math.random()*30;
  document.body.style.animationDelay='-'.concat(delay.toString(), 's');
}
