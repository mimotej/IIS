

var x = document.getElementById("report");
x.addEventListener("mouseover",function (){
    x.classList.add("hover")
})
x.addEventListener("mouseout",function (){
    x.classList.remove("hover")
})
/*
for(var i = 0; i < x.length; i++) {
  (function(index) {
    x[index].addEventListener("mouseover", function() {
           const y = document.getElementById("report");
           x.classList.toggle('hover');
     })
  })(i);
}*/