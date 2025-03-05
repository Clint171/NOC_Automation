function toggleMenu(){
    menuEl = document.querySelector(".menu-div");

    if(menuEl.style.display == "none"){
        menuEl.style.display = "flex"
    }
    else{
        menuEl.style.display = "none"
    }
}