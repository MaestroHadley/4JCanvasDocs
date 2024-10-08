// ==UserScript==
// @name         4J Tamper Tools
// @namespace    https://github.com/MaestroHadley/4JCanvasDocs
// @version      1.9
// @description  A Canvas UserScript for 4J specific tools.
// @author       Chad Scott (ChadScott@katyisd.org)
// @author       Nicholas Hadley (hadley_n@4j.lane.edu)
// @match        https://4j.instructure.com/*
// @match        https://4j.test.instructure.com/*
// @match        https://4j.beta.instructure.com/*
// @grant        none
// @updateURL    https://github.com/MaestroHadley/4JCanvasDocs/raw/main/CanvasScripts/4J_Tamper_Tools.user.js
// @downloadURL  https://github.com/MaestroHadley/4JCanvasDocs/raw/main/CanvasScripts/4J_Tamper_Tools.user.jsjs
// ==/UserScript==
(function() {
    'use strict';

    // Check if the current page is the dashboard and add the "See all courses" button
    if (/^\/\??[^\/]*\/?$/.test(window.location.pathname)) {
        waitForElement("#dashboard_header_container div.ic-Dashboard-header__actions", addDashboardAllCoursesButton);
    }
    // Check if the current page is the modules page and add the "Jump to Module" functionality
    if (/^\/courses\/[0-9]+\/modules\??[^\/]*\/?$/.test(window.location.pathname) ||
        /^\/courses\/[0-9]+\??[^\/]*\/?$/.test(window.location.pathname)) {
        waitForElement("#context_modules", addJumpToModuleSelection);
    }

    // Check if the current page is the /courses page and add filters, search, and sorting
    if (/^\/courses\??[^\/]*\/?$/.test(window.location.pathname)) {
        waitForElement("#content", () => {
            //addColumnSortsToAllCoursesTables();
            addSearchFiltersToAllCoursesTables(true, true); // Enable both search fields and filters
        });
    }

    // Function to add the "See all courses" button on the dashboard
    function addDashboardAllCoursesButton(headerActionsDiv) {
        var allCoursesLink = document.createElement("a");
        allCoursesLink.href = "/courses";
        allCoursesLink.classList.add("Button");
        allCoursesLink.innerText = "See all courses";
        allCoursesLink.style.marginRight = "1.5rem";

        headerActionsDiv.insertAdjacentElement("afterbegin", allCoursesLink);
    }
    // Utility function to wait for an element to be available in the DOM
    function waitForElement(selector, callback) {
        const element = document.querySelector(selector);
        if (element) {
            callback(element);
        } else {
            setTimeout(() => waitForElement(selector, callback), 100);
        }
    }

 // Function to add the "Jump to Module" functionality
    function addJumpToModuleSelection(contextModulesDiv) {
        if (contextModulesDiv) {
            createJumpToModuleMenu(contextModulesDiv);

            const moduleDivs = [
                ...document.querySelectorAll("#context_modules div.context_module"),
            ];
            addModuleLinksToMenu(moduleDivs);
        }
    }

    function addBackToTopButton(moduleDiv) {
        const containerDiv = document.createElement("div");
        containerDiv.classList.add("ski-container-back-top-button");
        containerDiv.style.textAlign = "right";
        containerDiv.style.padding = "9px";
        containerDiv.style.marginTop = "-0.5rem";
        containerDiv.style.marginBottom = "-0.5rem";
        containerDiv.dataset.associatedModuleId = `${moduleDiv?.dataset?.moduleId}`;
        containerDiv.innerHTML = `<a class="Button" href="modules"><i class="icon-line icon-arrow-up"></i> Back to Top</a>`;

        moduleDiv.insertAdjacentElement("beforeEnd", containerDiv);
    }

    function createJumpToModuleMenu(contextModulesDiv) {
        const jumpToModuleSelectionHTML = `
        <details id='ski-jump-to-module-menu' class='ski-ui' style="margin: 9px;">
            <summary>Jump to Module</summary>
            <ul></ul>
        </details>`;

        contextModulesDiv.insertAdjacentHTML(
            "beforebegin",
            jumpToModuleSelectionHTML
        );
    }

    function addModuleLinksToMenu(moduleDivs) {
        for (const moduleDiv of moduleDivs) {
            addModuleLinkToMenu(moduleDiv);
        }
    }

    function addModuleLinkToMenu(moduleDiv) {
        const jumpToModuleMenu = document.getElementById("ski-jump-to-module-menu");
        if (!jumpToModuleMenu) {
            return;
        }

        const menuList = jumpToModuleMenu.querySelector("ul");
        const moduleId = moduleDiv.id.split("_").pop();
        if (menuList && moduleId) {
            const moduleHeader = document.getElementById(`${moduleId}`);
            if (moduleHeader) {
                const moduleNameSpan = document.querySelector(
                    `#context_module_${moduleId} div.header span.name`
                );
                if (moduleNameSpan) {
                    const moduleName = moduleNameSpan.innerText;
                    if (moduleName) {
                        addBackToTopButton(moduleDiv);

                        const menuLinkItem = document.createElement("li");
                        menuLinkItem.innerHTML = `<a href='#context_module_${moduleId}'>${moduleName}</a>`;
                        menuList.insertAdjacentElement("beforeEnd", menuLinkItem);
                    }
                }
            }
        }

        jumpToModuleMenu.style.display = "";
    }

    function removeBackToTopContainer(moduleId) {
        const backToTopContainer = document.querySelector(
            `#context_modules div[data-associated-module-id='${moduleId}']`
        );
        backToTopContainer?.parentElement?.removeChild(backToTopContainer);
    }

    function removeLinkItem(moduleId) {
        const link = document.querySelector(
            `#ski-jump-to-module-menu li > a[href='#context_module_${moduleId}']`
        );
        const linkItem = link?.parentElement;
        linkItem?.parentElement?.removeChild(linkItem);
    }
    // Function to add column sorting to the /courses page tables
    function addColumnSortsToAllCoursesTables() {
        const courseTableIds = ["my_courses_table", "past_enrollments_table", "future_enrollments_table"];
        courseTableIds.forEach(courseTableId => {
            const table = document.getElementById(courseTableId);
            if (table) {
                const tableHeaders = table.querySelectorAll("thead tr th[scope='col']");
                tableHeaders.forEach(columnHeader => {
                    const columnNameClass = Array.from(columnHeader.classList).find(className =>
                        className.startsWith("course-list-") && className.endsWith("-column")
                    );
                    if (columnNameClass && !columnNameClass.includes("-star")) {
                        const columnCells = Array.from(table.querySelectorAll(`tbody tr td.${columnNameClass}`));
                        if (columnCells.length > 1) {
                            const headingName = columnHeader.innerText.trim();
                            columnHeader.innerHTML = `<button class="ski-ui-column-sort-btn" data-ski-sort-dir="none">${headingName}</button>`;
                            const columnSortButton = columnHeader.querySelector("button");
                            columnSortButton.addEventListener("click", () => {
                                const sortDirection = columnSortButton.dataset.skiSortDir;
                                columnSortButton.dataset.skiSortDir = sortDirection === "asc" ? "desc" : "asc";
                                Array.from(table.querySelectorAll("thead th button.ski-ui-column-sort-btn"))
                                    .filter(btn => btn !== columnSortButton)
                                    .forEach(btn => btn.dataset.skiSortDir = "none");
                                updateTableSortDisplay(courseTableId, columnNameClass, columnSortButton.dataset.skiSortDir === "asc");
                            });
                        }
                    }
                });
            }
        });
    }

    // Function to update table sorting display
    function updateTableSortDisplay(tableId, sortColumn, isOrderAscending) {
        const table = document.getElementById(tableId);
        if (table) {
            const tableBody = table.querySelector("tbody");
            const tableRows = Array.from(tableBody.querySelectorAll("tr.course-list-table-row"));
            if (tableRows.length > 1) {
                tableRows.sort((aRow, bRow) => {
                    const aCell = aRow.querySelector(`td.${sortColumn}`);
                    const bCell = bRow.querySelector(`td.${sortColumn}`);
                    return isOrderAscending
                        ? aCell.innerText.toUpperCase().localeCompare(bCell.innerText.toUpperCase())
                        : bCell.innerText.toUpperCase().localeCompare(aCell.innerText.toUpperCase());
                });
                tableRows.forEach(row => tableBody.appendChild(row));
            }
        }
    }

    // Function to add search filters to the /courses page tables
    function addSearchFiltersToAllCoursesTables(areSearchFieldsEnabled, areFiltersEnabled) {
        if (areSearchFieldsEnabled || areFiltersEnabled) {
            addSearchFiltersRowToAllCoursesTables();
            if (areSearchFieldsEnabled) addSearchFieldsToAllCoursesTables();
            if (areFiltersEnabled) addFiltersToAllCoursesTables();
        }
    }

    // Function to add the search filters row
    function addSearchFiltersRowToAllCoursesTables() {
        const courseTableIds = ["my_courses_table", "past_enrollments_table", "future_enrollments_table"];
        courseTableIds.forEach(courseTableId => {
            const coursesTable = document.getElementById(courseTableId);
            if (coursesTable) {
                const coursesTableHead = coursesTable.querySelector("thead");
                if (coursesTableHead) {
                    if (!coursesTableHead.querySelector("tr.ski-search-filters-row")) {
                        coursesTableHead.insertAdjacentHTML("beforeend", `
                            <tr class="ski-search-filters-row">
                                <td class="course-list-star-column"></td>
                                <td class="ski-column-search-field course-list-course-title-column course-list-no-left-border"></td>
                                <td class="ski-column-search-field course-list-nickname-column course-list-no-left-border"></td>
                                <td class="ski-column-filter-field course-list-term-column course-list-no-left-border"></td>
                                <td class="ski-column-filter-field course-list-enrolled-as-column course-list-no-left-border"></td>
                                <td class="ski-column-filter-field course-list-published-column course-list-no-left-border"></td>
                            </tr>
                        `);
                    }
                }
            }
        });
    }

    // Function to add search fields to the tables
    function addSearchFieldsToAllCoursesTables() {
        const courseTableIds = ["my_courses_table", "past_enrollments_table", "future_enrollments_table"];
        courseTableIds.forEach(courseTableId => {
            const coursesSearchAndFiltersRow = document.querySelector(`#${courseTableId} thead tr.ski-search-filters-row`);
            if (coursesSearchAndFiltersRow) {
                addSearchField(coursesSearchAndFiltersRow, "course-list-course-title-column", "ski-course-title-search", "Search course title");
                addSearchField(coursesSearchAndFiltersRow, "course-list-nickname-column", "ski-course-nickname-search", "Search nickname");
            }
        });
    }

    // Function to add individual search field
    function addSearchField(coursesSearchAndFiltersRow, columnClass, inputClass, placeholder) {
        const searchCell = coursesSearchAndFiltersRow.querySelector(`.ski-column-search-field.${columnClass}`);
        if (searchCell && !searchCell.querySelector(`.${inputClass}`)) {
            searchCell.insertAdjacentHTML("afterbegin", `<input type="text" class="${inputClass}" placeholder="${placeholder}" style="margin-bottom: 0;">`);
            const searchInput = searchCell.querySelector(`.${inputClass}`);
            if (searchInput) {
                searchInput.addEventListener("keyup", () => updateTableFilteredDisplay(searchCell.closest("table").id));
                searchInput.addEventListener("blur", () => updateTableFilteredDisplay(searchCell.closest("table").id));
            }
        }
    }

    // Function to add filters to the tables
    function addFiltersToAllCoursesTables() {
        const courseTableIds = ["my_courses_table", "past_enrollments_table", "future_enrollments_table"];
        courseTableIds.forEach(courseTableId => {
            const coursesSearchAndFiltersRow = document.querySelector(`#${courseTableId} thead tr.ski-search-filters-row`);
            if (coursesSearchAndFiltersRow) {
                addFilter(coursesSearchAndFiltersRow, "course-list-term-column", "ski-course-term-filter");
                addFilter(coursesSearchAndFiltersRow, "course-list-enrolled-as-column", "ski-course-role-filter");
                addFilter(coursesSearchAndFiltersRow, "course-list-published-column", "ski-course-published-filter");
            }
        });
    }

    // Function to add individual filter
    function addFilter(coursesSearchAndFiltersRow, columnClass, selectClass) {
        const filterCell = coursesSearchAndFiltersRow.querySelector(`.ski-column-filter-field.${columnClass}`);
        if (filterCell && !filterCell.querySelector(`.${selectClass}`)) {
            filterCell.insertAdjacentHTML("afterbegin", `<select class="${selectClass}"><option value="">All</option></select>`);
            const filterSelect = filterCell.querySelector(`.${selectClass}`);
            if (filterSelect) {
                const options = Array.from(new Set(Array.from(document.querySelectorAll(`#${filterCell.closest("table").id} tbody tr td.${columnClass}`)).map(cell => cell.innerText))).sort();
                options.forEach(option => filterSelect.insertAdjacentHTML("beforeend", `<option value="${option}">${option}</option>`));
                filterSelect.addEventListener("change", () => updateTableFilteredDisplay(filterCell.closest("table").id));
            }
        }
    }
    function updateTableFilteredDisplay(tableId) {
        const table = document.getElementById(tableId);
        if (table) {
            const searchAndFiltersRow = table.querySelector("thead tr.ski-search-filters-row");
            const filters = [];

            const searchCells = [
                ...searchAndFiltersRow.querySelectorAll("td.ski-column-search-field"),
            ];
            for (let searchCell of searchCells) {
                const searchInput = searchCell.querySelector("input");
                if (searchInput && !searchInput.disabled) {
                    const searchInputValue = new DOMParser().parseFromString(
                        searchInput.value,
                        "text/html"
                    ).body.innerText;
                    const columnNameClass = [...searchCell.classList].reduce(
                        (previousValue, currentValue) => {
                            if (
                                currentValue.startsWith("course-list-") &&
                                currentValue.endsWith("-column")
                            ) {
                                previousValue = currentValue;
                            }
                            return previousValue;
                        }
                    );

                    filters.push({
                        type: "search",
                        value: searchInputValue.trim(),
                        column: columnNameClass,
                    });
                }
            }

            const filterCells = [
                ...searchAndFiltersRow.querySelectorAll("td.ski-column-filter-field"),
            ];
            for (let filterCell of filterCells) {
                const selectInput = filterCell.querySelector("select");
                if (selectInput && !selectInput.disabled) {
                    const selectInputValue = new DOMParser().parseFromString(
                        selectInput.value,
                        "text/html"
                    ).body.innerText;
                    const columnNameClass = [...filterCell.classList].reduce(
                        (previousValue, currentValue) => {
                            if (
                                currentValue.startsWith("course-list-") &&
                                currentValue.endsWith("-column")
                            ) {
                                previousValue = currentValue;
                            }
                            return previousValue;
                        },
                        ""
                    );

                    filters.push({
                        type: "filter",
                        value: selectInputValue.trim(),
                        column: columnNameClass,
                    });
                }
            }

            if (searchAndFiltersRow) {
                const tableRows = [
                    ...table.querySelectorAll("tbody tr.course-list-table-row"),
                ];
                if (tableRows) {
                    for (let row of tableRows) {
                        let displayValue = "table-row";
                        for (let filter of filters) {
                            if (filter.value) {
                                const cellToCheck = row.querySelector(`.${filter.column}`);
                                if (cellToCheck) {
                                    if (filter.type == "search") {
                                        if (
                                            !cellToCheck.innerText
                                            .toUpperCase()
                                            .includes(filter.value.toUpperCase())
                                        ) {
                                            displayValue = "none";
                                            break;
                                        }
                                    } else if (filter.type == "filter") {
                                        if (filter.column.includes("-published-")) {
                                            if (
                                                cellToCheck.querySelector("span").innerText.trim() !=
                                                filter.value
                                            ) {
                                                displayValue = "none";
                                                break;
                                            }
                                        } else {
                                            if (cellToCheck.innerText.trim() != filter.value) {
                                                displayValue = "none";
                                                break;
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        row.style.display = displayValue;
                    }
                }
            }
        }
    }


function gatherFilters(searchAndFiltersRow) {
    const filters = [];
    searchAndFiltersRow.querySelectorAll("td.ski-column-search-field").forEach(searchCell => {
        const searchInput = searchCell.querySelector("input");
        if (searchInput && !searchInput.disabled) {
            filters.push({
                type: "search",
                value: searchInput.value.trim(),
                column: Array.from(searchCell.classList).find(className => className.startsWith("course-list-") && className.endsWith("-column"))
            });
        }
    });
    searchAndFiltersRow.querySelectorAll("td.ski-column-filter-field").forEach(filterCell => {
        const selectInput = filterCell.querySelector("select");
        if (selectInput && !selectInput.disabled) {
            filters.push({
                type: "filter",
                value: selectInput.value.trim(),
                column: Array.from(filterCell.classList).find(className => className.startsWith("course-list-") && className.endsWith("-column"))
            });
        }
    });
    console.log("Filters gathered:", filters);
    return filters;
}



    // Function to watch for the element by query
    function watchForElementByQuery(query, callback) {
        console.log("Watching for element:", query);
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    const element = document.querySelector(query);
                    if (element) {
                        observer.disconnect();
                        console.log("Element found:", element);
                        callback(element);
                    }
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });

        // Fallback if the element is already on the page
        const element = document.querySelector(query);
        if (element) {
            observer.disconnect();
            console.log("Element already present:", element);
            callback(element);
        }
    }

    var assocRegex = new RegExp('^/courses$');
    var assocRegex2 = new RegExp('^/accounts/([0-9]+)$');
    var acc = window.location.pathname;
    var errors = [];
    var parentId = [];
    var termId = '';
    var courses = {};
    var dedupThings = [];
    var wholeName = '';
    var array =[];
    var user = '';
    /* role setup: Change the roles you want to have access to the crosslisting features. assocRegex is for the button on the all courses page and assocRegex2 is for the admin page. */
    var roles = ENV.current_user_roles;
    var cxbuttonRoles = ["admin", "teacher", "root_admin"];
    var admincxbuttonRoles = ["admin", "root_admin"];
    var test1 = cxbuttonRoles.some(el => roles.includes(el));
    var test2 = admincxbuttonRoles.some(el => roles.includes(el));
    if( (test1 === true) && (assocRegex.test(window.location.pathname))){
        getCourses();
    }
    if( (test2 === true) && (assocRegex2.test(window.location.pathname))){
        add_buttonAdmin();
    }

    /* This adds the crosslist button to the all courses page and runs the function openDialog when clicked. */
    function add_button() {
        var parent = document.querySelector('div.ic-Action-header__Secondary');
        if (parent) {
            var el = parent.querySelector('#jj_cross');
            if (!el) {
                el = document.createElement('button');
                el.classList.add('Button','element_toggler');
                el.type = 'button';
                el.id = 'jj_cross';
                var icon = document.createElement('i');
                icon.classList.add('icon-sis-synced');
                el.appendChild(icon);
                var txt = document.createTextNode(' Crosslist Courses');
                el.appendChild(txt);
                el.addEventListener('click', openDialog);
                parent.appendChild(el);
            }
        }
    }
    /* This function creates the main popup window users interact with the crosslist their courses.
    I followed the Canvas Style Guide as much as possible to the CSS already available to create the form elements. */
        function createDialog() {
        var el = document.querySelector('#jj_cross_dialog');
        if (!el) {
            el = document.createElement('form');
            el.id = 'jj_cross_dialog';
            el.classList.add('ic-Form-group');
            //Parent Course selection
            var help = document.createElement('div');
            help.innerHTML = '<div class="grid-row middle-xs"><div class="col-lg-8"><div class="content-box">Directions: Complete for each step to crosslist and rename your courses.<br/>Click HELP for more information about Crosslisting.</div></div><div class="col-lg-4"><div id="action_helper" style="cursor: pointer" class="content-box"><div class="ic-image-text-combo Button" type="button"><i class="icon-info"></i><div class="ic-image-text-combo__text">Help</div></div></div></div></div>';
            help.classList.add('ic-Label');
            el.appendChild(help);
            var el5 = document.createElement('div');
            el5.classList.add('ic-Form-control');
            el.appendChild(el5);
            var label = document.createElement('label');
            label.htmlFor = 'jj_cross_parentCourse';
            label.innerHTML = '<a title="Parent Course:\nThe main course that all other classes will join.">Step 1: Select Parent Course</a>';
            label.classList.add('ic-Label');
            el5.appendChild(label);
            var select = document.createElement('select');
            select.id = 'jj_cross_parentCourse';
            select.classList.add('ic-Input');
            select.onchange = getChildren;
            el5.appendChild(select);
            //childcourse checkboxes
            var el6 = document.createElement('fieldset');
            el6.id = 'child_list';
            el6.style.visibility = 'hidden';
            el6.classList.add("ic-Fieldset", "ic-Fieldset--radio-checkbox");
            el.appendChild(el6);
            var el7 = document.createElement('legend');
            el7.classList.add('ic-Legend');
            el7.innerHTML = '<a title="Only choose courses that need the same course materials.">Step 2: Choose Child Courses to Crosslist Into Parent Course</a>';
            el6.appendChild(el7);
            var el8 = document.createElement('div');
            el8.id = 'checkboxes';
            el8.classList.add('ic-Checkbox-group');
            el6.appendChild(el8);
            //Course Name
            var el9 = document.createElement('div');
            el9.id = 'course_div';
            el9.style.visibility = 'hidden';
            el9.classList.add('ic-Form-control');
            el.appendChild(el9);
            label = document.createElement('label');
            label.htmlFor = 'course_name';
            label.innerHTML = '<a title="Naming Convention: Course Name Teacher - Year/Term "> Step 3: Set Course Name</a>';
            label.classList.add('ic-Label');
            el9.appendChild(label);
            var input = document.createElement('input');
            input.id = 'course_name';
            input.classList.add('ic-Input');
            input.type = 'text';
            //input.placeholder = 'Course Name Teacher - Year/Term';
            el9.appendChild(input);
            //Course Name Examples
            var el10 = document.createElement('p');
            el10.id = 'examples';
            el10.style.visibility = 'hidden';
            el10.classList = 'text-info';
            el.appendChild(el10);
            var ol = document.createElement('ol');
            ol.textContent = 'Examples:';
            //ol.style.border = "thin solid #0000FF";
            ol.classList = 'unstyled';
            el10.appendChild(ol);
            var li = document.createElement('li');
            li.textContent = 'AP Physics- Hadley - S1 24';
            ol.appendChild(li);
            li = document.createElement('li');
            li.textContent = 'Spanish 1- Hadley- S1/24';
            ol.appendChild(li);
            li = document.createElement('li');
            li.textContent = 'ELA - Hadley - Per 6 S1 ';
            ol.appendChild(li);
            //message flash
            var msg = document.createElement('div');
            msg.id = 'jj_cross_msg';
            //msg.classList.add('ic-flash-warning');
            msg.style.display = 'none';
            el.appendChild(msg);
            var parent = document.querySelector('body');
            parent.appendChild(el);
        }
        setParent();
            /* opens the help dialog window */
        document.getElementById("action_helper").addEventListener("click", function(){
            openHelp();
        });
    }

    /* Help dialog window, explains the steps of how to crosslist */
    function createhelpDialog(){
        var el = document.querySelector('#help_dialog');
        if (!el) {
            el = document.createElement('div');
            el.innerHTML= '<div><b>Crosslist and Name Course:</b> Complete all 3 steps <br/><b>Crosslist and Don\'t Rename Course:</b> Complete steps 1 and 2 <br/><b>Only Rename Course:</b> Complete steps 1 and 3<br/><br/>Hover over each step for more help.</div>';
            el.id = 'help_dialog';
            //Parent Course selection
            //message flash
            var msg = document.createElement('div');
            msg.id = 'jj_cross_msg';
            //msg.classList.add('ic-flash-warning');
            msg.style.display = 'none';
            el.appendChild(msg);
            var parent = document.querySelector('body');
            parent.appendChild(el);
        }
    }

    /* This function creates the modal window for the help dialog, I have hidden the titlebar close button and disabled the ability to esc close also. */
    function openHelp() {
        try {
            createhelpDialog();
            $('#help_dialog').dialog({
                'title' : 'Possible Actions',
                'autoOpen' : false,
                'closeOnEscape': false,
                'open': function () { $(".ui-dialog-titlebar-close").hide(); $(".ui-dialog").css("top", "10px");},
                'buttons' : [  {
                    'text' : 'Close',
                    'click' : function() {
                        $(this).dialog('destroy').remove();
                    }
                } ],
                'modal' : true,
                'resizable' : false,
                'height' : 'auto',
                'width' : '30%'
            });
            if (!$('#help_dialog').dialog('isOpen')) {
                $('#help_dialog').dialog('open');
            }
        } catch (e) {
            console.log(e);
        }
    }

    /* This function sends an api request to get the current users course list. */
    function getCourses(){
        // Reset global variable errors
        errors= [];
        var url = "/api/v1/users/self/courses?inlcude[]=term&include[]=sections&per_page=75";
        $.ajax({
            'async': true,
            'type': "GET",
            'global': true,
            'dataType': 'JSON',
            'data': JSON.stringify(courses),
            'contentType': "application/json",
            'url': url,
            'success': function(courses){
                dedupThings = Array.from(courses.reduce((m, t) => m.set(t.id, t), new Map()).values());
                add_button();
            }
        });
    }
    /* This function sorts and returns only the most recent term id number. This prevents users from crosslisting into manually created courses. */
    function getTerm(dedupThings, prop) {
        var max;
        for (var i=0 ; i<dedupThings.length ; i++) {
            if (!max || parseInt(dedupThings[i][prop]) > parseInt(max[prop]))
                max = dedupThings[i];
        }
        return max;
    }

    /* This function takes the return from getTerm and then filters the courses for only that term id and sets the courses in the dropdown. */
    function setParent(){
        var toAppend = '';
        var select = document.getElementById('jj_cross_parentCourse');
        select.options.length = 0; // clear out existing items
        var getMax = getTerm(dedupThings, "enrollment_term_id");
        termId = getMax.enrollment_term_id;
        $.each(dedupThings, function(i, o){
            if (o.enrollment_term_id == termId) {
                toAppend += '<option value="'+o.id+'">'+o.name+'</option>';
            }
        });
        var blank ='';
        blank += '<option value="">Please select</option>';
        $('#jj_cross_parentCourse').append(blank);
        $('#jj_cross_parentCourse').append(toAppend);
    }

    /* This function reveals the rest of the form after the parent course is selected. It adds the remaining courses not chosen to be the
    parent course as check boxes.*/
    function getChildren(){
        var show = document.getElementById('child_list');
        show.style.visibility = 'visible';
        var show2 = document.getElementById('course_div');
        show2.style.visibility = 'visible';
        var show3 = document.getElementById('examples');
        show3.style.visibility = 'visible';
        var clear = document.getElementById('checkboxes');
        var clear3='';
        if (clear.innerHTML !== null){
            clear.innerHTML = "";
        }
        parentId = document.getElementById("jj_cross_parentCourse").value;
        var labelAppend = '';
        var inputAppend = '';
        $.each(dedupThings,function(i,o){
            if (o.enrollment_term_id == termId && o.id != parentId) {
                labelAppend += '<input type="checkbox" id="'+o.id+'" name="childCourses" value="'+o.id+'">'+'<label class="ic-Label" for="'+o.id+'">'+o.name+'</label>';
                clear3=labelAppend;
                if (labelAppend !== null){
                    labelAppend = '';
                }
                inputAppend += '<div class="ic-Form-control ic-Form-control--checkbox">'+clear3+'</div>';
            }
        });
        $('#checkboxes').append(inputAppend);
    }
    /* Users are able to change the course name. This sets the text input to wholeName.*/
    function courseName(){
        var newName= [];
        newName = $.map($('input[id="course_name"]'), function(i){return i.value; });
        $.each(newName, function(index, item){
            if (item !==null){
                wholeName = item;
            }
        });
    }

    /* This functions sends an API command to change the name of the parent course.*/
    function updateName(){
        var url = "/api/v1/courses/" + parentId + "?course[name]=" + wholeName;
        $.ajax({
            'cache' : false,
            'url' : url ,
            'type' : 'PUT',
        }).done(function() {
            closeDialog();
        });
    }

    /* This function creates the modal window for the form dialog box */
    function openDialog() {
        try {
            createDialog();
            $('#jj_cross_dialog').dialog({
                'title' : 'Crosslist Courses',
                'autoOpen' : false,
                'closeOnEscape': false,
                'open': function () { $(".ui-dialog-titlebar-close").hide(); $(".ui-dialog").css("top", "10px");},
                'buttons' : [  {
                    'text' : 'Cancel',
                    'click' : function() {
                        $(this).dialog('destroy').remove();
                        errors = [];
                        updateMsgs();
                    }
                },{
                    'text' : 'Submit',
                    'class': 'Button Button--primary',
                    'click' : submitButton

                } ],
                'modal' : true,
                'resizable' : false,
                'height' : 'auto',
                'width' : '40%'
            });
            if (!$('#jj_cross_dialog').dialog('isOpen')) {
                $('#jj_cross_dialog').dialog('open');
            }
        } catch (e) {
            console.log(e);
        }
    }

    /* this function stores the courses checked in step 2 to the array variable */
    function setChild() {
        array = $.map($('input[name="childCourses"]:checked'), function(c){return c.value; });
    }
    /* This function sends an API command to crosslist the courses stored in the array variable with the parent course.
    When it's done, it will execute the function to set the course to the users dashboard and then close the window.*/
    function processDialog() {
        $.each(array, function(index,item){
            var childCourse = item;
            var childSection;
            var url = "/api/v1/courses/" + childCourse + "/sections?";
            $.ajax({
                'async': true,
                'type': "GET",
                'global': true,
                'dataType': 'JSON',
                'data': JSON.stringify(childSection),
                'contentType': "application/json",
                'url': url,
                'success': function (data) {
                    $.each(data, function(i,o){
                        childSection = o.id;
                        var url2 = "/api/v1/sections/" + childSection + "/crosslist/" + parentId +"?";
                        $.ajax({
                            'cache' : false,
                            'url' : url2 ,
                            'type' : 'POST',
                        }).done(function() {
                            setFavorite();
                            closeDialog();
                        });
                    });
                }
            });
        });
    }

    /* Sets the course to the user's dashboard */
    function setFavorite (){
        var url = "/api/v1/users/self/favorites/courses/" + parentId;
        $.ajax({
            'cache' : false,
            'url' : url ,
            'type' : 'POST',
        });
    }

    /* If the user omits step 3, a dialog windows pops up verifying if the user doesn't want to rename the course.
    The confirmation button says crosslist only. If the user does want to rename, they can hit close and rename it in step 3. */
    function nonameDialog(){
        var el = document.querySelector('#nonamedialog');
        if (!el) {
            el = document.createElement('div');
            el.id = 'nonamedialog';
            var el2 = document.createElement('div');
            el.appendChild(el2);
            var el3 = document.createElement('p');
            el3.textContent = ' No course name entered!';
            el2.appendChild(el3);
            //direction 1
            var div1 = document.createElement('div');
            div1.classList.add('ic-image-text-combo');
            el.appendChild(div1);
            var icon;
            icon = document.createElement('i');
            icon.classList.add('icon-check');
            div1.appendChild(icon);
            var text = document.createElement('div');
            text.classList.add("text-success","ic-image-text-combo__text");
            text.textContent = 'Click "Crosslist Only" to continue without naming';
            div1.appendChild(text);
            //direction 2
            div1 = document.createElement('div');
            div1.classList.add('ic-image-text-combo');
            el.appendChild(div1);
            icon = document.createElement('i');
            icon.classList.add('icon-warning');
            div1.appendChild(icon);
            text = document.createElement('p');
            text.classList.add("text-warning","ic-image-text-combo__text");
            text.textContent = 'Click "Cancel" to go back and name your course.';
            div1.appendChild(text);
            var parent = document.querySelector('body');
            parent.appendChild(el);
        }
    }
    /* This creates the modal window for the noname dialog box */
    function opennonameDialog(){
        try {
            nonameDialog();
            $('#nonamedialog').dialog({
                'title' : 'Crosslist Courses Only',
                'autoOpen' : false,
                'closeOnEscape': false,
                'open': function () { $(".ui-dialog-titlebar-close").hide(); },
                'buttons' : [{
                    'text' : 'Cancel',
                    'click' : function() {
                        $(this).dialog('destroy').remove();
                        errors = [];
                        updateMsgs();
                    }
                },{
                    'text' : 'Crosslist Only',
                    'class': 'Button Button--primary',
                    'click' : processDialog
                } ],
                'modal' : true,
                'resizable' : false,
                'height' : 'auto',
                'width' : '40%',
            });
            if (!$('#nonamedialog').dialog('isOpen')) {
                $('#nonamedialog').dialog('open');
            }
        } catch (e) {
            console.log(e);
        }
    }
    /* If the user omits step 2, a dialog windows pops up verifying if the user doesn't want to crosslist any courses.
    The confirmation button says rename only. If the user does want to crosslist, they can hit close and choose courses to crosslist in step 2. */
    function nocrossDialog(){
        var el = document.querySelector('#nocrossdialog');
        if (!el) {
            el = document.createElement('div');
            el.id = 'nocrossdialog';
            var el2 = document.createElement('div');
            el.appendChild(el2);
            var el3 = document.createElement('p');
            el3.textContent = ' No courses selected to crosslist!';
            el2.appendChild(el3);
            //direction 1
            var div1 = document.createElement('div');
            div1.classList.add('ic-image-text-combo');
            el.appendChild(div1);
            var icon;
            icon = document.createElement('i');
            icon.classList.add('icon-check');
            div1.appendChild(icon);
            var text = document.createElement('div');
            text.classList.add("text-success","ic-image-text-combo__text");
            text.textContent = 'Click "Update Name" to continue without crosslisting';
            div1.appendChild(text);
            //direction 2
            div1 = document.createElement('div');
            div1.classList.add('ic-image-text-combo');
            el.appendChild(div1);
            icon = document.createElement('i');
            icon.classList.add('icon-warning');
            div1.appendChild(icon);
            text = document.createElement('p');
            text.classList.add("text-warning","ic-image-text-combo__text");
            text.textContent = 'Click "Cancel" to go back and choose courses to crosslist.';
            div1.appendChild(text);
            var parent = document.querySelector('body');
            parent.appendChild(el);
        }
    }
    /* Creates the modal window for the nocross dialog box */
    function opennocrossDialog(){
        try {
            nocrossDialog();
            $('#nocrossdialog').dialog({
                'title' : 'Update Course Name Only',
                'autoOpen' : false,
                'closeOnEscape': false,
                'open': function () { $(".ui-dialog-titlebar-close").hide(); },
                'buttons' : [  {
                    'text' : 'Cancel',
                    'click' : function() {
                        $(this).dialog('destroy').remove();
                        errors = [];
                        updateMsgs();
                    }
                },{
                    'text' : 'Update Name',
                    'class': 'Button Button--primary',
                    'click' : updateName
                } ],
                'modal' : true,
                'resizable' : false,
                'height' : 'auto',
                'width' : '40%'
            });
            if (!$('#nocrossdialog').dialog('isOpen')) {
                $('#nocrossdialog').dialog('open');
            }
        } catch (e) {
            console.log(e);
        }
    }
    /* This function processes the request of the main crosslist dialog window. It executes the appropriate functions based on steps completed.
    If step 2 and step 3 are skipped, it throws an error stating to complete step 2 and or step 3. */
    function submitButton(){
        errors = [];
        courseName();
        setChild();
        if (wholeName !=='' || array !=+ ''){
            if (wholeName !=='' && array !=+ ''){
                updateName();
                processDialog();
            } else if (wholeName ==='' && array !=+ ''){
                opennonameDialog();
            }else{
                opennocrossDialog();
            }
        }else{
            errors.push('You must choose a course to crosslist or input a course name.');
            updateMsgs();
        }
    }
    /* This function closes all dialog windows and launches a success dialog */
    function closeDialog(){
        $('#nocrossDialog').dialog('close');
        $('#nonameDialog').dialog('close');
        $('#jj_cross_dialog').dialog('close');
        $('#jj_cross_dialog2').dialog('close');
        window.location.reload(true);
        open_success_dialog();
    }
    /* This creates error messages at the bottom of the crosslist dialog window */
    function updateMsgs() {
        var msg = document.getElementById('jj_cross_msg');
        if (!msg) {
            return;
        }
        if (msg.hasChildNodes()) {
            msg.removeChild(msg.childNodes[0]);
        }
        if (typeof errors === 'undefined' || errors.length === 0) {
            msg.style.display = 'none';
        } else {
            var div1 = document.createElement('div');
            div1.classList.add('ic-flash-error');
            var div2;
            div2 = document.createElement('div');
            div2.classList.add('ic-flash__icon');
            div2.classList.add('aria-hidden="true"');
            div1.appendChild(div2);
            var icon;
            icon = document.createElement('i');
            icon.classList.add('icon-warning');
            div2.appendChild(icon);
            var ul = document.createElement('ul');
            for (var i = 0; i < errors.length; i++) {
                var li;
                li = document.createElement('li');
                li.textContent = errors[i];
                ul.appendChild(li);
            }
            div1.appendChild(ul);
            var button;
            button = document.createElement('button');
            button.type = 'button';
            button.classList.add("Button", "Button--icon-action", "close_link");
            div1.appendChild(button);
            icon = document.createElement('i');
            icon.classList.add('ic-icon-x');
            icon.classList.add('aria-hidden="true"');
            button.appendChild(icon);
            msg.appendChild(div1);
            msg.style.display = 'inline-block';
        }
    }
    /* This creates the success dialog window */
    function successDialog(){
        var el = document.querySelector('#success_dialog');
        if (!el) {
            el = document.createElement('div');
            el.id = 'success_dialog';
            var div1 = document.createElement('div');
            div1.classList.add('ic-flash-success');
            el.appendChild(div1);
            var div2 = document.createElement('div');
            div2.classList.add('ic-flash__icon');
            div2.classList.add('aria-hidden="true"');
            div1.appendChild(div2);
            var icon = document.createElement('i');
            icon.classList.add('icon-check');
            div2.appendChild(icon);
            var msg = document.createTextNode("The action completed successfully!");
            div1.appendChild(msg);
            var button = document.createElement('button');
            button.type = 'button';
            button.classList.add("Button", "Button--icon-action", "close_link");
            el.appendChild(button);
            icon = document.createElement('i');
            icon.classList.add('ic-icon-x');
            icon.classList.add('aria-hidden="true"');
            button.appendChild(icon);
            var parent = document.querySelector('body');
            parent.appendChild(el);
        }
    }

    /* This creates the modal window for the success dialog and it closes with the page refresh in the closeDialog function */
    function open_success_dialog(){
        try {
            successDialog();
            $('#success_dialog').dialog({
                'autoOpen' : false,
                'closeOnEscape': false,
                'open': function () { $(".ui-dialog-titlebar").hide(); $(".ui-widget-content").css("background", "rgba(255, 255, 255, 0)"); $(".ui-dialog.ui-widget-content").css("box-shadow", "none");},
                'modal' : true,
                'resizable' : false,
                'height' : 'auto',
                'width' : '40%',
            });
            if (!$('#success_dialog').dialog('isOpen')) {
                $('#success_dialog').dialog('open');
            }
        } catch (e) {
            console.log(e);
        }
    }



})();
