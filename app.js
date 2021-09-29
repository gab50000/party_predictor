selectors = document.getElementsByClassName("party-selector");

function create_radio_action(element) {
  return function (event) {
    console.log(element);
    let party = element.getAttribute("value");
    let politician_id = document
      .getElementById("politician_id")
      .getAttribute("value");
    console.log(party);
    console.log(politician_id);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/guess_party", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(
      JSON.stringify({
        id: politician_id,
        party: party,
      })
    );
  };
}

for (element of selectors) {
  element.addEventListener("click", create_radio_action(element));
}

document.getElementById("refresh").addEventListener("click", function (event) {
  location.reload();
});

// .addEventListener("click", function(elem){
//     alert("click")
// })
