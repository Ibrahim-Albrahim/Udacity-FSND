deleteBtns = document.querySelectorAll(".danger");

for (let i = 0; i < deleteBtns.length; i++) {
    const deleteBtn = deleteBtns[i];
    deleteBtn.onclick = function (e) {
        const galleryId = e.target.parentElement.dataset.id;
        fetch("/" + galleryId + "/delete", {
            method: "DELETE"})
            .then(function () {
                const gallery = e.target.parentElement.parentElement;
                gallery.remove();})
            .catch(function (e) {
                console.error(e);});
    };
}


