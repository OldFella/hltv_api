const input = document.getElementById('searchInput');
const ul = document.getElementById('folderList');
const liList = ul.getElementsByTagName('li');

input.addEventListener('keyup', function() {
const filter = input.value.toLowerCase();
for (let i = 0; i < liList.length; i++) {
    const text = liList[i].innerText.toLowerCase();
    liList[i].style.display = text.includes(filter) ? '' : 'none';
}
});