function createMyPlannerNow() {
  // 1. Створюємо нову таблицю на Google Диску
  var ss = SpreadsheetApp.create("🎯 Мій Персональний Планер");
  var sheet = ss.getActiveSheet();
  sheet.setName("Фокус дня");

  // 2. Вимикаємо сітку
  sheet.setHiddenGridlines(true);

  // 3. Ширина колонок
  sheet.setColumnWidth(1, 25);
  sheet.setColumnWidth(2, 50);
  sheet.setColumnWidth(3, 280);
  sheet.setColumnWidth(4, 160);

  // 4. Головний банер
  sheet.getRange("B2:D2").merge()
       .setValue("🎯 ПЕРСОНАЛЬНИЙ ДАШБОРД")
       .setFontFamily("Roboto").setFontSize(13).setFontWeight("bold")
       .setFontColor("#FFFFFF").setBackground("#0F172A")
       .setHorizontalAlignment("center").setVerticalAlignment("middle");
  sheet.setRowHeight(2, 40);

  // 5. Дата та прогрес
  sheet.getRange("B3").setFormula('=UPPER(TEXT(TODAY(); "dddd, dd mmmm"))')
       .setFontColor("#64748B").setFontSize(10);
  sheet.getRange("C3").setValue("Прогрес:").setHorizontalAlignment("right").setFontWeight("bold");
  sheet.getRange("D3").setFormula('=TEXT(COUNTIF(B5:B12; TRUE)/MAX(1; COUNTA(C5:C12)); "0%") & " ЗАКРИТО"')
       .setFontWeight("bold").setFontColor("#10B981");

  // 6. Блок головного завдання
  sheet.getRange("B4:D4").merge().setValue("⭐ ГОЛОВНЕ ЗАВДАННЯ ДНЯ").setFontWeight("bold").setBackground("#F1F5F9");
  sheet.getRange("B5").setDataValidation(SpreadsheetApp.newDataValidation().requireCheckbox().build());
  sheet.getRange("C5").setValue("Закрити ключовий робочий пріоритет");
  sheet.getRange("D5").setValue("Фокус: 90 хв").setFontColor("#64748B");

  // 7. Блок звичок
  sheet.getRange("B7:D7").merge().setValue("⚡ ЩОДЕННІ ЗВИЧКИ").setFontWeight("bold").setBackground("#F1F5F9");
  var habits = [
    "Склянка води після пробудження",
    "20 хвилин читання або навчання",
    "Спорт / фізична активність",
    "Вечірній підсумок дня"
  ];

  for (var i = 0; i < habits.length; i++) {
    var r = 8 + i;
    sheet.getRange("B" + r).setDataValidation(SpreadsheetApp.newDataValidation().requireCheckbox().build());
    sheet.getRange("C" + r).setValue(habits[i]);
    sheet.getRange("D" + r).setValue("Звичка").setFontColor("#64748B");
  }

  // Відкриваємо доступ за посиланням
  var file = DriveApp.getFileById(ss.getId());
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.EDIT);

  // Виводимо посилання в Журнал виконання
  Logger.log("ТАБЛИЦЮ СТВОРЕНО\n УСПІШНО!");
  Logger.log("Посилання: " + ss.getUrl());
}
