window.addEventListener('load', () => {

    let displayBuyer = $('.stats-cost-buyer').length > 0;
    let sorting = {'revenue': '', 'cost': '', 'stats': ''}
    let costs, revenues;
    let totalCosts = 0;
    let totalRevenues = 0;
    let stats = {};
    let statsArr = [];
    let buyers = [];
    $('.stats-buyer.active').each((i, block) => buyers.push(parseInt(block.id.replace('buyer-', ''))));

    const filterByDate = (startDate, endDate) => {
        $.ajax({
            method: "get",
            url: "/main/filter_by_date/",
            data: {start_date: startDate, end_date: endDate},
            success: (data) => {
                allCosts = JSON.parse(data['costs']);
                allRevenues = JSON.parse(data['revenues']);
                setData();
            },
            error: (data) => {
            }
        });
    }

    $('#daterangepicker').daterangepicker(
        {
            locale: {
                format: 'YYYY-MM-DD'
            }
        }, 
        function(start, end, label) {
            let startDate = start.format('YYYY-MM-DD');
            let endDate = end.format('YYYY-MM-DD');
            filterByDate(startDate, endDate);
            $('.stats-date.active').removeClass('active');
            $('#daterangepicker').addClass('active');
            $('.stats-chosen-date').html(startDate + ' - ' + endDate);
        }
    );

    $('.stats-date.standart').on('click', (e) => {
        filterByDate(e.target.id, e.target.id);
        $('.stats-date.active').removeClass('active');
        e.target.classList.add('active');
        $('.stats-chosen-date').html(e.target.id);
    })

    const getCostHtmlString = (cost) => {
        return `<tr class="stats-cost">
                    <td><div class="stats-status${cost.fields.definitive ? ' definitive' : ''}"></div>${cost.fields.date}</td>
                    ${displayBuyer ? `<td>${cost.fields.ad.buyer_id}</td>` : ''}
                    <td>${cost.fields.ad.cabinet_pk}</td>
                    <td class="stats-td-number">${cost.fields.amount } ${cost.fields.ad.currency}</td>
                    <td class="stats-td-number">${cost.fields.amount_USD} USD</td>
                    <td class="stats-td-number">${cost.fields.clicks}</td>
                    <td class="stats-td-number">${cost.fields.cost_per_unique_click}</td>
                    <td class="stats-td-number">${cost.fields.cpc}</td>
                    <td class="stats-td-number">${cost.fields.cpm}</td>
                    <td class="stats-td-number">${cost.fields.ctr}</td>
                    <td class="stats-td-number">${cost.fields.impressions}</td>
                    <td>${cost.fields.objective}</td>
                    <td class="stats-td-number">${cost.fields.quality_score_ectr}</td>
                    <td class="stats-td-number">${cost.fields.quality_score_ecvr}</td>
                    <td class="stats-td-number">${cost.fields.quality_score_organic}</td>
                    <td>${cost.fields.results}</td>
                </tr>`;
    }

    const fillCosts = () => {
        let htmlString = '';
        totalCosts = 0;
        let totalClicks = 0;
        let totalViews = 0;
        for(let cost of costs) {
            htmlString += cost.htmlString;
            totalCosts += cost.fields.amount_USD;
            totalClicks += cost.fields.clicks;
            totalViews += cost.fields.views;

            let buyerId = cost.fields.ad.buyer_id;
            if(!Object.keys(stats).includes(buyerId)) {
                stats[buyerId] = {};
            }
            let date = cost.fields.date;
            if(!Object.keys(stats[buyerId]).includes(date)) {
                stats[buyerId][date] = {"costs": cost.fields.amount_USD, "revenues": 0};
            } else {
                stats[buyerId][date]['costs'] += cost.fields.amount_USD;
            }
        }
        totalCosts = Math.round(totalCosts * 100) / 100;
        if(!sorting['cost']) {
            $('.stats-cost').remove();
            $('.stats-costs-header').after(htmlString);
        } else {
            $(`#${sorting['cost']}`).click();
        }
        $('#costs-total-amount').html(totalCosts + ' USD');
        $('#costs-total-clicks').html(totalClicks);
        $('#costs-total-views').html(totalViews);
    }

    const getRevenueHtmlString = (revenue) => {
        return `<tr class="stats-revenue">
                    <td><div class="stats-status${revenue.fields.definitive ? ' definitive' : ''}"></div>${revenue.fields.datetime}</td>
                    ${displayBuyer ? `<td>${revenue.fields.buyer[1]}</td>` : ''}
                    <td class="stats-td-number">${revenue.fields.amount} USD</td>
                    <td class="stats-td-number">${revenue.fields.clicks}</td>
                    <td class="stats-td-number">${revenue.fields.conversions}</td>
                    <td class="stats-td-number">${revenue.fields.sales}</td>
                    <td>${revenue.fields.sub_id}</td>
                    <td>${revenue.fields.sub_id_1}</td>
                    <td>${revenue.fields.sub_id_2}</td>
                    <td>${revenue.fields.sub_id_3}</td>
                    <td>${revenue.fields.sub_id_5}</td>
                    <td>${revenue.fields.sub_id_6}</td>
                    <td>${revenue.fields.sub_id_7}</td>
                    <td>${revenue.fields.sub_id_8}</td>
                    <td class="stats-td-number">${revenue.fields.sub_id_9}</td>
                    <td>${revenue.fields.sub_id_10}</td>
                    <td>${revenue.fields.sub_id_11}</td>
                    <td>${revenue.fields.sub_id_12}</td>
                    <td>${revenue.fields.campaign}</td>
                    <td>${revenue.fields.campaign_group}</td>
                    <td class="stats-td-number">${revenue.fields.campaign_id}</td>
                    <td class="stats-td-number">${revenue.fields.campaign_unique_clicks}</td>
                    <td>${revenue.fields.country}</td>
                    <td>${revenue.fields.country_code}</td>
                    <td>${revenue.fields.offer}</td>
                    <td>${revenue.fields.os_icon}</td>
                    <td>${revenue.fields.os_version}</td>
                </tr>`;
    }

    const fillRevenues = () => {
        let htmlString = '';
        totalRevenues = 0;
        let totalClicks = 0;
        let totalConversions = 0;
        let totalSales = 0;
        for(let revenue of revenues) {
            htmlString += revenue.htmlString;
            totalRevenues += revenue.fields.amount;
            totalClicks += revenue.fields.clicks;
            totalConversions += revenue.fields.conversions;
            totalSales += revenue.fields.sales;

            let buyerId = revenue.fields.buyer[1];
            if(!Object.keys(stats).includes(buyerId)) {
                stats[buyerId] = {};
            }
            let date = revenue.fields.datetime.slice(0, 10);
            if(!Object.keys(stats[buyerId]).includes(date)) {
                stats[buyerId][date] = {"costs": 0, "revenues": revenue.fields.amount};
            } else {
                stats[buyerId][date]['revenues'] += revenue.fields.amount;
            }
        }
        totalRevenues = Math.round(totalRevenues * 100) / 100;
        if(!sorting['revenue']) {
            $('.stats-revenue').remove();
            $('.stats-revenues-header').after(htmlString);
        } else {
            $(`#${sorting['revenue']}`).click();
        }
        $('#revenues-total-amount').html(totalRevenues + ' USD');
        $('#revenues-total-clicks').html(totalClicks);
        $('#revenues-total-conversions').html(totalConversions);
        $('#revenues-total-sales').html(totalSales);
    }

    const getStatHtmlString = (stat) => {
        return `<tr class="stats-stats">
                    <td>${stat.date}</td>
                    ${displayBuyer ? `<td>${stat.buyer}</td>` : ''}
                    <td class="stats-td-number">${stat.revenues}</td>
                    <td class="stats-td-number">${stat.costs}</td>
                    <td class="stats-td-number">${stat.profit}</td>
                    <td class="stats-td-number">${stat.roi}</td>
                </tr>`;
    }

    const fill = () => {
        stats = {};
        statsArr = [];
        fillCosts();
        fillRevenues();
        let htmlString = '';
        for(let [buyer, buyerData] of Object.entries(stats)) {
            for(let [date, dateData] of Object.entries(buyerData)) {
                dateData['revenues'] = Math.round(dateData['revenues'] * 100) / 100;
                dateData['costs'] = Math.round(dateData['costs'] * 100) / 100;
                let profit = Math.round((dateData['revenues'] - dateData['costs']) * 100) / 100;
                let roi = dateData['costs'] != 0 ? Math.round((profit / dateData['costs']) * 10000) / 100 : '-';
                let stat = {'buyer': buyer, 'date': date, 'profit': profit, 'roi': roi, ...dateData};
                statsArr.push(stat);
                htmlString += getStatHtmlString(stat);
            }
        }
        if(!sorting['stats']) {
            $(`.stats-stats`).remove();
            $('.stats-stats-header').after(htmlString);
        } else {
            $(`#${sorting['stats']}`).click();
        }
        $('#stats-total-revenues').html(totalRevenues);
        $('#stats-total-costs').html(totalCosts);
        $('#stats-total-profit').html(Math.round((totalRevenues - totalCosts) * 100) / 100);
        $('#stats-total-roi').html(totalCosts != 0 ? Math.round(((totalRevenues - totalCosts) / totalCosts) * 10000) / 100 : '-');
    }

    const setData = () => {
        for(let cost of allCosts) {
            cost['htmlString'] = getCostHtmlString(cost);
        }
        for(let revenue of allRevenues) {
            if(revenue.fields.buyer == null) {
                revenue.fields.buyer = ['null', '-'];
                if(!buyers.includes('null')) {
                    buyers.push('null');
                }
            }
            revenue['htmlString'] = getRevenueHtmlString(revenue);
        }
        costs = [...allCosts];
        revenues = [...allRevenues];
        fill();
    }

    $('.stats-arrow:not(.stats)').on('click', (e) => {
        let [model, field, direction] = e.target.id.split('-');
        sorting[model] = e.target.id;
        let obj = model == 'cost' ? costs : revenues;
        if(direction == 'asc') {
            if(field == 'buyer') {
                if(model == 'cost') {
                    obj.sort((a, b) => a.fields.ad['buyer_id'] > b.fields.ad['buyer_id'] ? 1 : -1);
                } else {
                    obj.sort((a, b) => a.fields.buyer[1] > b.fields.buyer[1] ? 1 : -1);
                }
            } else if(field == 'cabinet') {
                obj.sort((a, b) => a.fields.ad['cabinet_pk'] > b.fields.ad['cabinet_pk'] ? 1 : -1);
            } else {
                obj.sort((a, b) => a.fields[field] > b.fields[field] ? 1 : -1);
            }
        } else {
            if(field == 'buyer') {
                if(model == 'cost') {
                    obj.sort((a, b) => a.fields.ad['buyer_id'] < b.fields.ad['buyer_id'] ? 1 : -1);
                } else {
                    obj.sort((a, b) => a.fields.buyer[1] < b.fields.buyer[1] ? 1 : -1);
                }
            } else if(field == 'cabinet') {
                obj.sort((a, b) => a.fields.ad['cabinet_pk'] < b.fields.ad['cabinet_pk'] ? 1 : -1);
            } else {
                obj.sort((a, b) => a.fields[field] < b.fields[field] ? 1 : -1);
            }
        }
        let htmlString = model == 'cost' ? costs.map((cost) => getCostHtmlString(cost)).join() : revenues.map((revenue) => getRevenueHtmlString(revenue)).join();
        $(`.stats-${model}`).remove();
        $(`.stats-${model}s-header`).after(htmlString);
        $(`.stats-${model}s-header .stats-arrow.active`).removeClass('active');
        e.target.classList.add('active');
    })

    $('.stats-arrow.stats').on('click', (e) => {
        sorting['stats'] = e.target.id;
        let [model, field, direction] = e.target.id.split('-');
        if(direction == 'asc') {
            statsArr.sort((a, b) => a[field] > b[field] ? 1 : -1);
        } else {
            statsArr.sort((a, b) => a[field] < b[field] ? 1 : -1);
        }
        let htmlString = statsArr.map((stat) => getStatHtmlString(stat)).join();
        $(`.stats-stats`).remove();
        $(`.stats-stats-header`).after(htmlString);
        $(`.stats-stats-header .stats-arrow.active`).removeClass('active');
        e.target.classList.add('active');
    })

    $('.stats-buyer').on('click', (e) => {
        let id = parseInt(e.target.id.replace('buyer-', ''));
        if(buyers.includes(id)) {
            buyers.splice(buyers.indexOf(id), 1);
            e.target.classList.remove('active');
        } else {
            buyers.push(id);
            e.target.classList.add('active');
        }
        costs = allCosts.filter((cost) => buyers.includes(cost.fields.ad.buyer_pk));
        revenues = allRevenues.filter((revenue) => buyers.includes(revenue.fields.buyer[0]));
        fill();
    })

    $('.stats-update').on('click', (e) => {
        let type = e.target.id.replace('update-', '');
        $(`.stats-update-loading.${type}`).css('display', '');
        e.target.style.display = 'none';
        const token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "post",
            url: `/main/get_${type}/`,
            data: {csrfmiddlewaretoken: token},
            success: (data) => {
                if(type == 'costs') {
                    allCosts = JSON.parse(data['costs']);
                } else {
                    allRevenues = JSON.parse(data['revenues']);
                }
                setData();

                $(`.stats-update-loading.${type}`).css('display', 'none');
                e.target.style.display = '';
                let datetime = data['update'];
                let date = datetime.slice(0, 10).split('-').reverse().join('.');
                let update = `${date} ${datetime.slice(11, 16)}`;
                $(`#last-update-${type}`).html(update);
            },
            error: (data) => {
            }
        });
    })

    setData();
})