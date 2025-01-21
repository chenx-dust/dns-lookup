// DNS 状态码转换函数
function getStatusText(status) {
    const statusCodes = {
        0: 'NOERROR - 没有错误',
        1: 'FORMERR - 格式错误',
        2: 'SERVFAIL - 服务器失败',
        3: 'NXDOMAIN - 不存在的域名',
        4: 'NOTIMP - 未实现',
        5: 'REFUSED - 查询被拒绝',
        6: 'YXDOMAIN - 域名不应存在',
        7: 'YXRRSET - RR集不应存在',
        8: 'NXRRSET - RR集不存在',
        9: 'NOTAUTH - 服务器未授权',
        10: 'NOTZONE - 域名不在区域中'
    };
    return statusCodes[status] || `未知状态(${status})`;
}

// DNS 记录类型转换函数
function getDNSType(type) {
    const types = {
        1: 'A',
        2: 'NS',
        5: 'CNAME',
        6: 'SOA',
        12: 'PTR',
        15: 'MX',
        16: 'TXT',
        28: 'AAAA',
        33: 'SRV',
        257: 'CAA'
    };
    return types[type] || `TYPE${type}`;
}

// 获取本机 IP
document.getElementById('getMyIp').addEventListener('click', async function() {
    const button = this;
    const spinner = document.getElementById('ipSpinner');
    const customEcsInput = document.getElementById('customEcs');
    
    // 显示加载状态
    button.disabled = true;
    spinner.classList.remove('d-none');
    
    try {
        const response = await fetch('/api/ip');
        const data = await response.json();
        customEcsInput.value = data.ip;
    } catch (error) {
        alert('获取IP地址失败：' + error.message);
    } finally {
        // 恢复按钮状态
        button.disabled = false;
        spinner.classList.add('d-none');
    }
});

// DNS 查询表单提交
document.getElementById('dnsForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const domain = document.getElementById('domain').value;
    const queryType = document.getElementById('queryType').value;
    const customEcs = document.getElementById('customEcs').value;

    const resultArea = document.getElementById('queryResult');
    resultArea.textContent = '正在查询中...';

    try {
        // 构建查询 URL
        const params = new URLSearchParams({
            name: domain,
            type: queryType === 'ALL' ? '255' : queryType,
        });

        // 如果设置了 ECS，添加到参数中
        if (customEcs) {
            params.append('edns_client_subnet', customEcs);
        }

        // 发送请求到本地后端
        const response = await fetch(`/api/resolve?${params.toString()}`);
        const data = await response.json();

        // 格式化结果
        let result = '<div class="result-header">';
        result += `<p><strong>查询状态:</strong> ${getStatusText(data.Status)}</p>`;
        result += `<p><strong>域名:</strong> ${domain}</p>`;
        result += `<p><strong>查询类型:</strong> ${queryType}</p>`;
        if (data.edns_client_subnet) {
            result += `<p><strong>ECS:</strong> ${data.edns_client_subnet}</p>`;
        }
        result += '</div>';

        if (data.Answer) {
            result += '<div class="section-title">查询结果</div>';
            data.Answer.forEach(record => {
                result += '<div class="dns-record">';
                result += `<div class="dns-record-header">${getDNSType(record.type)} 记录</div>`;
                result += '<div class="dns-record-content">';
                result += `<div class="dns-record-label">名称:</div><div class="dns-record-value">${record.name}</div>`;
                result += `<div class="dns-record-label">类型:</div><div class="dns-record-value">${getDNSType(record.type)}</div>`;
                result += `<div class="dns-record-label">TTL:</div><div class="dns-record-value">${record.TTL} 秒</div>`;
                result += `<div class="dns-record-label">数据:</div><div class="dns-record-value">${record.data}</div>`;
                result += '</div></div>';
            });
        } else if (data.Authority) {
            result += '<div class="section-title">权威记录</div>';
            data.Authority.forEach(record => {
                result += '<div class="dns-record">';
                result += `<div class="dns-record-header">${getDNSType(record.type)} 记录</div>`;
                result += '<div class="dns-record-content">';
                result += `<div class="dns-record-label">名称:</div><div class="dns-record-value">${record.name}</div>`;
                result += `<div class="dns-record-label">类型:</div><div class="dns-record-value">${getDNSType(record.type)}</div>`;
                result += `<div class="dns-record-label">TTL:</div><div class="dns-record-value">${record.TTL} 秒</div>`;
                result += `<div class="dns-record-label">数据:</div><div class="dns-record-value">${record.data}</div>`;
                result += '</div></div>';
            });
        } else {
            result += '<div class="section-title">查询结果</div>';
            result += '<div class="dns-record">未找到记录</div>';
        }

        if (data.Comment) {
            result += `<div class="section-title">注释</div>`;
            result += `<div class="dns-record">${data.Comment}</div>`;
        }

        resultArea.innerHTML = result;
    } catch (error) {
        resultArea.textContent = '查询出错：' + error.message;
    }
}); 