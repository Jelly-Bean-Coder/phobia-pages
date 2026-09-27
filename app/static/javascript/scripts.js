const source = new EventSource("/js-event-stream");
const token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

let alertCounter = 0;

function newFlashMessage(message, type) {
    const template = document.getElementById("template");
    if (!template) return;

    // 1. Define allowed alert types (fallback to 'primary' if invalid)
    const validTypes = ['success', 'danger', 'warning', 'info', 'secondary'];
    const alertType = validTypes.includes(type) ? type : 'primary';

    // Incremented ID for targetting this specific alert instance
    const currentId = `alert-${alertCounter++}`;

    // 2. Set the HTML string inside the template content container securely
    template.innerHTML = `
      <div id="${currentId}" class="alert alert-${alertType} alert-dismissible fade show position-absolute top-0 start-50 translate-middle-x w-100 z-3 mt-3 custom-slow-fade" role="alert" style="z-index: 1050;">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;

    // 3. Stamp it out onto the page
    document.body.appendChild(template.content.cloneNode(true));

    // 4. Handle the automatic slow fade out and DOM removal
    setTimeout(() => {
        const alertElement = document.getElementById(currentId);
        if (alertElement) {
            // Trigger visual opacity fade-out
            alertElement.classList.remove('show');

            // Completely delete from DOM after CSS transition finishes (1.5 seconds)
            setTimeout(() => {
                alertElement.remove();
            }, 1500);
        }
    }, 2000); // Stays visible for 3 seconds before starting the fade
}

async function bookmark(phobia_id) {
    const params = new URLSearchParams({
        phobia_id: phobia_id
    });
    let bookmark = await fetch(`/create_bookmark?${params}`,);
    let status = bookmark.status

    let el = document.getElementById("bookmark-star");

    if (status === 201) {
        el.classList.add("bookmark-created");
        newFlashMessage("Bookmark created!", "success");
    }
    else if (status === 200) {
        el.classList.remove("bookmark-created");
        newFlashMessage("Bookmark removed!", "success");
    }
}

function selectPillOption(button, position, value) {
      // Slide the background
      document.getElementById('pill-bg').style.transform = `translateX(${position}%)`;

      let monthlyBilling = document.getElementById('monthly-row');
      let yearlyBilling = document.getElementById('yearly-row');

      // Toggle colors
      const buttons = button.parentElement.querySelectorAll('.btn');
      buttons.forEach(btn => { btn.classList.replace('text-white', 'text-secondary'); });
      button.classList.replace('text-secondary', 'text-white');

      // TRACKING: This variable now holds the active selection
      console.log("User selected option:", value);

      if (value == "yearly") {

            yearlyBilling.classList.remove("d-none");


            monthlyBilling.classList.add("d-none");

        } else {

            monthlyBilling.classList.remove("d-none");

            yearlyBilling.classList.add("d-none");
        }
    }


async function deleteLog(log_id) {
    try {
        // Send a POST request with the log_id in the JSON body
        let logDelete = await fetch(`/delete_log`,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                },
                body:JSON.stringify({log_id: log_id}),
            });

        let status = logDelete.status;
        let el = document.getElementById(`log-${log_id}`);

        if (status === 200) {
            // Check if the element actually exists before trying to remove it
            if (el) {
                el.remove();
                location.reload()
            }
            newFlashMessage("Log deleted successfully!", "success");
        } else {
            newFlashMessage("Error deleting log!", "danger");
            console.log(`Failed to delete log with ID ${log_id}. Status code: ${status}. Error: ${await logDelete.text()}`);
        }
    } catch (error) {
        // Catches network errors or server crashes
        console.error("Network error:", error);
        newFlashMessage("Network error. Please try again.", "danger");
    }
}


source.addEventListener("flash", (e) => {
    const data = JSON.parse(e.data);
    newFlashMessage(data.message, data.type); // Calls your function!
});

const form = document.getElementById('logsForm');

form.addEventListener('submit', function (event) {
  // If the form is invalid, stop it from submitting
  if (!form.checkValidity()) {
    event.preventDefault();
    event.stopPropagation();
  }

  // Add the Bootstrap class to visually trigger the red/green alerts
  form.classList.add('was-validated');
});
