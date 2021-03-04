# Open Healthcare Statistics

<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: 2021-03-04 10:53:21</p>

---

<table border="1" class="dataframe summary">
  <thead>
    <tr style="text-align: right;">
      <th>org</th>
      <th>repo count</th>
      <th>size</th>
      <th>stargazers</th>
      <th>watchers</th>
      <th>forks</th>
      <th>open_issues</th>
      <th>top license</th>
      <th>top language</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>111Online</th>
      <td>13</td>
      <td>520454</td>
      <td>10</td>
      <td>10</td>
      <td>0</td>
      <td>25</td>
      <td>Apache License 2.0</td>
      <td>C#</td>
    </tr>
    <tr>
      <th>NHSDigital</th>
      <td>30</td>
      <td>100935</td>
      <td>49</td>
      <td>49</td>
      <td>40</td>
      <td>200</td>
      <td>MIT License</td>
      <td>Python</td>
    </tr>
    <tr>
      <th>nhsconnect</th>
      <td>30</td>
      <td>646417</td>
      <td>96</td>
      <td>96</td>
      <td>69</td>
      <td>162</td>
      <td>Apache License 2.0</td>
      <td>CSS</td>
    </tr>
    <tr>
      <th>nhsengland</th>
      <td>23</td>
      <td>36117</td>
      <td>13</td>
      <td>13</td>
      <td>38</td>
      <td>79</td>
      <td>MIT License</td>
      <td>Python</td>
    </tr>
    <tr>
      <th>nhsuk</th>
      <td>30</td>
      <td>417065</td>
      <td>55</td>
      <td>55</td>
      <td>43</td>
      <td>58</td>
      <td>MIT License</td>
      <td>HTML</td>
    </tr>
    <tr>
      <th>nhsx</th>
      <td>30</td>
      <td>540686</td>
      <td>2380</td>
      <td>2380</td>
      <td>531</td>
      <td>82</td>
      <td>MIT License</td>
      <td>Python</td>
    </tr>
  </tbody>
</table>

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
        .then(function (data) {
            appendData(data);
        })
        .catch(function (err) {
            console.log('error: ' + err);
        });
    function appendData(data) {
        var mainContainer = document.getElementById("NHSX");
        for (var i = 0; i < data.length; i++) {
            var div = document.createElement("div");
            div.innerHTML = data[i].name;
            mainContainer.appendChild(div);
        }
    }
</script>
<br/>

---

<center>fin</center>
