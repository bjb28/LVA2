// Sets the nave bar active based on the provided argument.

function setActiveNavItem(newPageId) {
  // Remove the 'active' class from all navbar items
  const navbarItems = document.querySelectorAll(".nav-item.nav-link");
  navbarItems.forEach((item) => {
    item.classList.remove("active");
  });

  // Add the 'active' class to the selected navbar item
  const selectedNavItem = document.getElementById(newPageId);
  if (selectedNavItem) {
    selectedNavItem.classList.add("active");
  }
}
