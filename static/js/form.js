// JavaScript để hiển thị spinner khi submit form
function showSpinner() {{
    document.getElementById("spinner").style.display = "block"; // Hiển thị spinner
    document.querySelector('.translating-message').style.display = 'block';
}}
function hintSpinner() {{
    document.getElementById("spinner").style.display = "none"; // Ẩn spinner
    document.querySelector('.translating-message').style.display = 'none';
}}
function validateForm() {{
    const srcLang = document.getElementById('src_lang').value;
    const trgLang = document.getElementById('trg_lang').value;
    const errorMessage = document.getElementById('error-message');
    errorMessage.style.display = 'none';

    // Kiểm tra nếu ngôn ngữ nguồn và đích giống nhau
    if (srcLang === trgLang) {{
        errorMessage.style.display = 'block'; // Hiển thị thông báo lỗi
        return false; // Ngừng gửi form
    }} else {{
        showSpinner(); // Hiển thị spinner khi form hợp lệ
        return true; // Gửi form
    }}
}}

// async function handleFormSubmit(event) {{
//     event.preventDefault(); // Ngừng gửi form mặc định

//     // Kiểm tra tính hợp lệ của form
//     if (!validateForm()) {{
//         return; // Nếu không hợp lệ, không gửi form
//     }}

//     const formData = new FormData(event.target);

//     // const response = await fetch("/translate/", {
//     //     method: "POST",
//     //     body: formData,
//     // });
    
//     try {{
//         const response = await fetch("/translate/", {
//             method: "POST",
//             body: formData,
//         });
//         console.log("no error")

//         if (response.ok) {{
//             // Ẩn spinner và thông báo "Translating..."
//             hintSpinner();

//             // Lấy tên file từ header hoặc body (ví dụ: trong Content-Disposition)
//             const contentDisposition = response.headers.get('Content-Disposition');
//             const filenameMatch = contentDisposition && contentDisposition.match(/filename="(.+)"/);
//             const filename = filenameMatch ? filenameMatch[1] : "translated_file"; // Nếu không có, dùng tên mặc định
            
//             console.log("create filename ok")

//             // Xử lý phản hồi (ví dụ, hiển thị file đã dịch)
//             const downloadUrl = URL.createObjectURL(await response.blob());
//             console.log("downloadurl ok")

//             const link = document.createElement("a");
//             link.href = downloadUrl;
//             link.download = filename;  // Đặt tên file sau khi dịch
//             link.click();

//             console.log("completed!")
//         }} else {{
//             // Hiển thị lỗi nếu có
//             alert("Error during translation.");
//         }}
//     }} catch (error) {{
//         console.error("Error:", error);
//         alert("An error occurred while processing the request.");
//     }}
// }}

async function handleFormSubmit(event) {
    event.preventDefault(); // Ngừng hành động mặc định của form

    // Kiểm tra tính hợp lệ của form
    if (!validateForm()) {
        return; // Nếu không hợp lệ, dừng xử lý
    }

    // Sau khi thành công, cho phép hành động mặc định (submit)
    event.target.submit(); // Reload hoặc redirect trang dựa trên action của form

}
