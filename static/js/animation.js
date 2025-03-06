document.querySelectorAll(".graph-card").forEach(card =>{
    card.addEventListener("click" , ()=>{
    }) 
});

function toggleMenu(){
    menuEl = document.querySelector(".menu-div");

    if(menuEl.style.display == "none"){
        menuEl.style.display = "flex"
    }
    else{
        menuEl.style.display = "none"
    }
}

function toggleCardOut(){
    document.querySelectorAll(".card-clicked").forEach(card =>{
        card.classList.remove("card-clicked");
    })
}