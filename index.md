# Open Healthcare Statistics

<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: 2021-03-04 10:53:21</p>

---

## [NHSX](https://github.com/nhsx)

#### Logo

<img src="https://avatars.githubusercontent.com/u/47388472?v=4" width="50"/>

### Open Repos

<div id="NHSX"></div>
<script>
    fetch('github_api/nhsx_repos.json')
        .then(function (response) {
            return response.json();
        })
        .then(function (datax) {
            appendData(datax);
        })
        .catch(function (err) {
            console.log('error: ' + err);
        });
    function appendData(datax) {
        var mainContainer = document.getElementById("NHSX");
        for (var i = 0; i < datax.length; i++) {
            var div = document.createElement("div");
            div.innerHTML = datax[i].name;
            mainContainer.appendChild(div);
        }
    }
</script>
<br/>

---

## [NHS Digital](https://github.com/NHSDigital)

#### Logo

<img src="https://avatars.githubusercontent.com/u/6683590?v=4" width="50"/>

### Open Repos

<div id="NHSD"></div>
<script>
    fetch('github_api/nhsdigital_repos.json')
        .then(function (response) {
            return response.json();
        })
        .then(function (datad) {
            appendData(datad);
        })
        .catch(function (err) {
            console.log('error: ' + err);
        });
    function appendData(datad) {
        var mainContainer = document.getElementById("NHSD");
        for (var i = 0; i < datad.length; i++) {
            var div = document.createElement("div");
            div.innerHTML = datad[i].name;
            mainContainer.appendChild(div);
        }
    }
</script>
<br/>

---

<center>fin</center>
