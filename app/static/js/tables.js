// Budget Revenue DataTables function
$(document).ready(function () {
    $('a[class="btn btn-info showTable"]').click(function () {
        $('div[class="card mb-4"]').show();
        $('a[class="btn btn-secondary hideTable"]').show();
        $('a[class="btn btn-info showTable"]').hide();

        var table = $('#revenue-summary-table').DataTable({
            serverSide: true,
            ajax: {
                url: '/api/data',
                data: {
                    loc_path: (function (data) {
                        data = window.location.pathname;
                        return data;
                    }())
                }
            },
            columns: [{
                data: "id",
                orderable: false
            },
                {
                    data: "revenue_date"
                },
                {
                    data: "revenue_value"
                },
                {
                    data: "revenue_source",
                    orderable: false
                },
                {
                    data: "entry_options",
                    orderable: false
                },
            ],
        });
    });
    $('a[class="btn btn-secondary hideTable"]').click(function () {
        $('#revenue-summary-table').DataTable().destroy();
        $('div[class="card mb-4"]').hide();
        $('a[class="btn btn-secondary hideTable"]').hide();
        $('a[class="btn btn-info showTable"]').show();
    });
});


// Budget Expense DataTables function.
$(document).ready(function () {
    $('a[class="btn btn-info showTable"]').click(function () {
        $('div[class="card mb-4"]').show();
        $('a[class="btn btn-secondary hideTable"]').show();
        $('a[class="btn btn-info showTable"]').hide();
        var table = $('#expense-summary-table').DataTable({
            serverSide: true,
            ajax: {
                url: '/api/data',
                data: {
                    loc_path: (function (data) {
                        data = window.location.pathname;
                        return data;
                    }())
                }
            },
            columns: [{
                data: "id",
                orderable: false
            },
                {
                    data: "expense_date"
                },
                {
                    data: "expense_item"
                },
                {
                    data: "expense_value"
                },
                {
                    data: "expense_item_category",
                    orderable: false
                },
                {
                    data: "expense_source",
                    orderable: false
                },
                {
                    data: "entry_options",
                    orderable: false
                },
            ],
        });
    });
    $('a[class="btn btn-secondary hideTable"]').click(function () {
        $('#expense-summary-table').DataTable().destroy();
        $('div[class="card mb-4"]').hide();
        $('a[class="btn btn-secondary hideTable"]').hide();
        $('a[class="btn btn-info showTable"]').show();
    });
});

// Budget Savings DataTables function
$(document).ready(function () {
    $('a[class="btn btn-info showTable"]').click(function () {
        $('div[class="card mb-4"]').show();
        $('a[class="btn btn-secondary hideTable"]').show();
        $('a[class="btn btn-info showTable"]').hide();
        var table = $('#savings-summary-table').DataTable({
            serverSide: true,
            ajax: {
                url: '/api/data',
                data: {
                    loc_path: (function (data) {
                        data = window.location.pathname;
                        return data;
                    }())
                }
            },
            columns: [{
                data: "id",
                orderable: false
            },
                {
                    data: "saving_date"
                },
                {
                    data: "saving_value"
                },
                {
                    data: "saving_source",
                    orderable: false
                },
                {
                    data: "saving_reason",
                    orderable: false
                },
                {
                    data: "saving_action",
                    orderable: false
                },
                {
                    data: "entry_options",
                    orderable: false
                }
            ],
        });
    });
    $('a[class="btn btn-secondary hideTable"]').click(function () {
        $('#savings-summary-table').DataTable().destroy();
        $('div[class="card mb-4"]').hide();
        $('a[class="btn btn-secondary hideTable"]').hide();
        $('a[class="btn btn-info showTable"]').show();
    });
});


// Budget Utilities DataTables function
$(document).ready(function () {
    $('a[class="btn btn-info showTable"]').click(function () {
        $('div[class="card mb-4"]').show();
        $('a[class="btn btn-secondary hideTable"]').show();
        $('a[class="btn btn-info showTable"]').hide();

        var table = $('#utilities-summary-table').DataTable({
            serverSide: true,
            ajax: {
                url: '/api/data',
                data: {
                    loc_path: (function (data) {
                        data = window.location.pathname;
                        return data;
                    }())
                }
            },
            columns: [{
                data: "id",
                orderable: false
            },
                {
                    data: "utilities_date"
                },
                {
                    data: "utilities_rent_value"
                },
                {
                    data: "utilities_energy_value"
                },
                {
                    data: "utilities_satellite_value"
                },
                {
                    data: "utilities_maintenance_value"
                },
                {
                    data: "budget_source"
                },
                {
                    data: "utilities_info",
                    orderable: false
                },
                {
                    data: "entry_options",
                    orderable: false
                },
            ],
        });
    });
    $('a[class="btn btn-secondary hideTable"]').click(function () {
        $('#utilities-summary-table').DataTable().destroy();
        $('div[class="card mb-4"]').hide();
        $('a[class="btn btn-secondary hideTable"]').hide();
        $('a[class="btn btn-info showTable"]').show();
    });
});


// Budget Tables DataTables function
$(document).ready(function () {

    $(document).ready(function () {
        $('a[class="btn btn-info showTableExpense"]').click(function () {
            $('div[class="card-body expense"]').show();
            $('a[class="btn btn-secondary hideTableExpense"]').show();
            $('a[class="btn btn-info showTableExpense"]').hide();
            var expense_table = $('#summary-expense-table').DataTable({
                serverSide: true,
                ajax: {
                    url: '/api/data',
                    data: {
                        loc_path: '/budget/new-expense-entry'
                    }
                },
                columns: [{
                    data: "id",
                    orderable: false
                },
                    {
                        data: "expense_date"
                    },
                    {
                        data: "expense_item"
                    },
                    {
                        data: "expense_value"
                    },
                    {
                        data: "expense_item_category",
                        orderable: false
                    },
                    {
                        data: "expense_source",
                        orderable: false
                    },
                ],
            });
        });
        $('a[class="btn btn-secondary hideTableExpense"]').click(function () {
            $('#summary-expense-table').DataTable().destroy();
            $('div[class="card-body expense"]').hide();
            $('a[class="btn btn-secondary hideTableExpense"]').hide();
            $('a[class="btn btn-info showTableExpense"]').show();
        });
    });

    $(document).ready(function () {
        $('a[class="btn btn-info showTableRevenue"]').click(function () {
            $('div[class="card-body revenue"]').show();
            $('a[class="btn btn-secondary hideTableRevenue"]').show();
            $('a[class="btn btn-info showTableRevenue"]').hide();
            var revenue_table = $('#summary-revenue-table').DataTable({
                serverSide: true,
                ajax: {
                    url: '/api/data',
                    data: {
                        loc_path: '/budget/new-revenue-entry'
                    }
                },
                columns: [{
                    data: "id",
                    orderable: false
                },
                    {
                        data: "revenue_date"
                    },
                    {
                        data: "revenue_value"
                    },
                    {
                        data: "revenue_source",
                        orderable: false
                    },
                ],
            });
        });
        $('a[class="btn btn-secondary hideTableRevenue"]').click(function () {
            $('#summary-revenue-table').DataTable().destroy();
            $('div[class="card-body revenue"]').hide();
            $('a[class="btn btn-secondary hideTableRevenue"]').hide();
            $('a[class="btn btn-info showTableRevenue"]').show();
        });
    });

    $(document).ready(function () {
        $('a[class="btn btn-info showTableSavings"]').click(function () {
            $('div[class="card-body savings"]').show();
            $('a[class="btn btn-secondary hideTableSavings"]').show();
            $('a[class="btn btn-info showTableSavings"]').hide();
            var savings_table = $('#summary-savings-table').DataTable({
                serverSide: true,
                ajax: {
                    url: '/api/data',
                    data: {
                        loc_path: '/budget/new-savings-entry'
                    }
                },
                columns: [{
                    data: "id",
                    orderable: false
                },
                    {
                        data: "saving_date"
                    },
                    {
                        data: "saving_value"
                    },
                    {
                        data: "saving_source",
                        orderable: false
                    },
                    {
                        data: "saving_reason",
                        orderable: false
                    },
                    {
                        data: "saving_action",
                        orderable: false
                    },
                ],
            });
        });
        $('a[class="btn btn-secondary hideTableSavings"]').click(function () {
            $('#summary-savings-table').DataTable().destroy();
            $('div[class="card-body savings"]').hide();
            $('a[class="btn btn-secondary hideTableSavings"]').hide();
            $('a[class="btn btn-info showTableSavings"]').show();
        });
    });

    $(document).ready(function () {
        $('a[class="btn btn-info showTableUtilities"]').click(function () {
            $('div[class="card-body utilities"]').show();
            $('a[class="btn btn-secondary hideTableUtilities"]').show();
            $('a[class="btn btn-info showTableUtilities"]').hide();
            var savings_table = $('#summary-utilities-table').DataTable({
                serverSide: true,
                ajax: {
                    url: '/api/data',
                    data: {
                        loc_path: '/budget/new-utilities-entry'
                    }
                },
                columns: [{
                    data: "id",
                    orderable: false
                },
                    {
                        data: "utilities_date"
                    },
                    {
                        data: "utilities_rent_value"
                    },
                    {
                        data: "utilities_energy_value"
                    },
                    {
                        data: "utilities_satellite_value"
                    },
                    {
                        data: "utilities_maintenance_value"
                    },
                    {
                        data: "utilities_info",
                        orderable: false
                    },
                    {
                        data: "budget_source",
                        orderable: false
                    },

                ],
            });
        });
        $('a[class="btn btn-secondary hideTableUtilities"]').click(function () {
            $('#summary-utilities-table').DataTable().destroy();
            $('div[class="card-body utilities"]').hide();
            $('a[class="btn btn-secondary hideTableUtilities"]').hide();
            $('a[class="btn btn-info showTableUtilities"]').show();
        });
    });
});