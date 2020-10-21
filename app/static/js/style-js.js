var report = document.getElementById("report");
report.addEventListener("mouseover", function () {
    report.classList.add("hover");
})
report.addEventListener("mouseout",function (){
        report.classList.remove("hover");
    })

var manage_users = document.getElementById("manage-users");
manage_users.addEventListener("mouseover", function () {
    manage_users.classList.add("hover");
})
manage_users.addEventListener("mouseout",function (){
        manage_users.classList.remove("hover");
    })
var modal_hide = document.getElementById('md01');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal_hide) {
        modal_hide.style.display = "none";
    }
}
document.getElementById("pencil").addEventListener("click",function (){
    var x= document.getElementsByClassName('edit-user-form-input');
    for (let i = 0; i < x.length; i++) {
        if(x[i].style.display=='block'){
            x[i].style.display='none';
        }
        else {
            x[i].style.display = 'block';
        }
    }
    })
