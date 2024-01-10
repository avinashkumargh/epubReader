function loadNextPage(){
    console.log("Im the function")
    var request = new XMLHttpRequest()
    console.log("loaded xmlhttp")
    request.open("GET", "/nextPage/", true)
    request.send()
}
/* 
document.addEventListener("keypress", function(event) {
    console.log(event.keyCode);
    nextPage = document.getElementById("nextpagebutton")
    if (event.keyCode == 39) {
        nextPage.click()
    }
});

document.onkeydown = function(event) {
    console.log(event.keyCode);
    nextPage = document.getElementById("nextpagebutton")
    if (event.keyCode == 39) {
        nextPage.click()
    }
} */