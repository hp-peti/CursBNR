namespace CursBNR
{
	partial class CursForm
	{
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		/// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null))
			{
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region Windows Form Designer generated code

		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{
			this.dateCurs = new System.Windows.Forms.DateTimePicker();
			this.btnGet = new System.Windows.Forms.Button();
			this.cbCurr = new System.Windows.Forms.ComboBox();
			this.lblCurs = new System.Windows.Forms.Label();
			this.tableLayoutPanel1 = new System.Windows.Forms.TableLayoutPanel();
			this.tableLayoutPanel2 = new System.Windows.Forms.TableLayoutPanel();
			this.tbRonResult = new System.Windows.Forms.TextBox();
			this.lblCurrValue = new System.Windows.Forms.Label();
			this.lblRonValue = new System.Windows.Forms.Label();
			this.tbRonValue = new System.Windows.Forms.TextBox();
			this.tbCurrValue = new System.Windows.Forms.TextBox();
			this.tbCurrResult = new System.Windows.Forms.TextBox();
			this.lblCurrResult = new System.Windows.Forms.Label();
			this.lblRonResult = new System.Windows.Forms.Label();
			this.btnTrend = new System.Windows.Forms.Button();
			this.tableLayoutPanel1.SuspendLayout();
			this.tableLayoutPanel2.SuspendLayout();
			this.SuspendLayout();
			// 
			// dateCurs
			// 
			this.dateCurs.Anchor = System.Windows.Forms.AnchorStyles.None;
			this.dateCurs.Format = System.Windows.Forms.DateTimePickerFormat.Short;
			this.dateCurs.Location = new System.Drawing.Point(3, 4);
			this.dateCurs.Name = "dateCurs";
			this.dateCurs.Size = new System.Drawing.Size(100, 20);
			this.dateCurs.TabIndex = 0;
			// 
			// btnGet
			// 
			this.btnGet.Anchor = System.Windows.Forms.AnchorStyles.None;
			this.btnGet.Location = new System.Drawing.Point(109, 3);
			this.btnGet.Name = "btnGet";
			this.btnGet.Size = new System.Drawing.Size(75, 22);
			this.btnGet.TabIndex = 3;
			this.btnGet.Text = "Get";
			this.btnGet.UseVisualStyleBackColor = true;
			this.btnGet.Click += new System.EventHandler(this.btnGet_Click);
			// 
			// cbCurr
			// 
			this.cbCurr.Anchor = System.Windows.Forms.AnchorStyles.None;
			this.cbCurr.DisplayMember = "IdMoneda";
			this.cbCurr.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
			this.cbCurr.FormattingEnabled = true;
			this.cbCurr.Location = new System.Drawing.Point(190, 3);
			this.cbCurr.Name = "cbCurr";
			this.cbCurr.Size = new System.Drawing.Size(80, 21);
			this.cbCurr.TabIndex = 4;
			this.cbCurr.ValueMember = "Value";
			this.cbCurr.SelectionChangeCommitted += new System.EventHandler(this.cbIdMoneda_SelectionChangeCommitted);
			// 
			// lblCurs
			// 
			this.lblCurs.AutoSize = true;
			this.lblCurs.Dock = System.Windows.Forms.DockStyle.Fill;
			this.lblCurs.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.lblCurs.Location = new System.Drawing.Point(276, 0);
			this.lblCurs.Name = "lblCurs";
			this.lblCurs.Size = new System.Drawing.Size(75, 28);
			this.lblCurs.TabIndex = 5;
			this.lblCurs.Text = "0";
			this.lblCurs.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// tableLayoutPanel1
			// 
			this.tableLayoutPanel1.ColumnCount = 5;
			this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
			this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
			this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
			this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50F));
			this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
			this.tableLayoutPanel1.Controls.Add(this.dateCurs, 0, 0);
			this.tableLayoutPanel1.Controls.Add(this.lblCurs, 3, 0);
			this.tableLayoutPanel1.Controls.Add(this.btnGet, 1, 0);
			this.tableLayoutPanel1.Controls.Add(this.cbCurr, 2, 0);
			this.tableLayoutPanel1.Controls.Add(this.tableLayoutPanel2, 0, 1);
			this.tableLayoutPanel1.Controls.Add(this.btnTrend, 4, 0);
			this.tableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill;
			this.tableLayoutPanel1.Location = new System.Drawing.Point(0, 0);
			this.tableLayoutPanel1.Name = "tableLayoutPanel1";
			this.tableLayoutPanel1.RowCount = 2;
			this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle());
			this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50F));
			this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20F));
			this.tableLayoutPanel1.Size = new System.Drawing.Size(435, 106);
			this.tableLayoutPanel1.TabIndex = 6;
			// 
			// tableLayoutPanel2
			// 
			this.tableLayoutPanel2.ColumnCount = 4;
			this.tableLayoutPanel1.SetColumnSpan(this.tableLayoutPanel2, 5);
			this.tableLayoutPanel2.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.98039F));
			this.tableLayoutPanel2.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
			this.tableLayoutPanel2.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 49.01961F));
			this.tableLayoutPanel2.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
			this.tableLayoutPanel2.Controls.Add(this.tbRonResult, 2, 0);
			this.tableLayoutPanel2.Controls.Add(this.lblCurrValue, 1, 0);
			this.tableLayoutPanel2.Controls.Add(this.lblRonValue, 1, 1);
			this.tableLayoutPanel2.Controls.Add(this.tbRonValue, 0, 1);
			this.tableLayoutPanel2.Controls.Add(this.tbCurrValue, 0, 0);
			this.tableLayoutPanel2.Controls.Add(this.tbCurrResult, 2, 1);
			this.tableLayoutPanel2.Controls.Add(this.lblCurrResult, 3, 1);
			this.tableLayoutPanel2.Controls.Add(this.lblRonResult, 3, 0);
			this.tableLayoutPanel2.Dock = System.Windows.Forms.DockStyle.Fill;
			this.tableLayoutPanel2.Location = new System.Drawing.Point(3, 31);
			this.tableLayoutPanel2.Name = "tableLayoutPanel2";
			this.tableLayoutPanel2.RowCount = 3;
			this.tableLayoutPanel2.RowStyles.Add(new System.Windows.Forms.RowStyle());
			this.tableLayoutPanel2.RowStyles.Add(new System.Windows.Forms.RowStyle());
			this.tableLayoutPanel2.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20F));
			this.tableLayoutPanel2.Size = new System.Drawing.Size(429, 72);
			this.tableLayoutPanel2.TabIndex = 6;
			// 
			// tbRonResult
			// 
			this.tbRonResult.Dock = System.Windows.Forms.DockStyle.Top;
			this.tbRonResult.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold);
			this.tbRonResult.Location = new System.Drawing.Point(220, 3);
			this.tbRonResult.Name = "tbRonResult";
			this.tbRonResult.ReadOnly = true;
			this.tbRonResult.Size = new System.Drawing.Size(151, 30);
			this.tbRonResult.TabIndex = 12;
			// 
			// lblCurrValue
			// 
			this.lblCurrValue.AutoSize = true;
			this.lblCurrValue.Dock = System.Windows.Forms.DockStyle.Fill;
			this.lblCurrValue.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.lblCurrValue.Location = new System.Drawing.Point(166, 0);
			this.lblCurrValue.Name = "lblCurrValue";
			this.lblCurrValue.Size = new System.Drawing.Size(48, 36);
			this.lblCurrValue.TabIndex = 7;
			this.lblCurrValue.Text = "EUR";
			this.lblCurrValue.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// lblRonValue
			// 
			this.lblRonValue.AutoSize = true;
			this.lblRonValue.Dock = System.Windows.Forms.DockStyle.Fill;
			this.lblRonValue.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.lblRonValue.Location = new System.Drawing.Point(166, 36);
			this.lblRonValue.Name = "lblRonValue";
			this.lblRonValue.Size = new System.Drawing.Size(48, 36);
			this.lblRonValue.TabIndex = 10;
			this.lblRonValue.Text = "RON";
			this.lblRonValue.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// tbRonValue
			// 
			this.tbRonValue.Dock = System.Windows.Forms.DockStyle.Top;
			this.tbRonValue.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold);
			this.tbRonValue.Location = new System.Drawing.Point(3, 39);
			this.tbRonValue.Name = "tbRonValue";
			this.tbRonValue.Size = new System.Drawing.Size(157, 30);
			this.tbRonValue.TabIndex = 8;
			this.tbRonValue.Text = "100";
			this.tbRonValue.TextChanged += new System.EventHandler(this.tbRonValue_TextChanged);
			// 
			// tbCurrValue
			// 
			this.tbCurrValue.Dock = System.Windows.Forms.DockStyle.Top;
			this.tbCurrValue.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold);
			this.tbCurrValue.Location = new System.Drawing.Point(3, 3);
			this.tbCurrValue.Name = "tbCurrValue";
			this.tbCurrValue.Size = new System.Drawing.Size(157, 30);
			this.tbCurrValue.TabIndex = 9;
			this.tbCurrValue.Text = "100";
			this.tbCurrValue.TextChanged += new System.EventHandler(this.tbCurrValue_TextChanged);
			// 
			// tbCurrResult
			// 
			this.tbCurrResult.Dock = System.Windows.Forms.DockStyle.Top;
			this.tbCurrResult.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold);
			this.tbCurrResult.Location = new System.Drawing.Point(220, 39);
			this.tbCurrResult.Name = "tbCurrResult";
			this.tbCurrResult.ReadOnly = true;
			this.tbCurrResult.Size = new System.Drawing.Size(151, 30);
			this.tbCurrResult.TabIndex = 11;
			// 
			// lblCurrResult
			// 
			this.lblCurrResult.AutoSize = true;
			this.lblCurrResult.Dock = System.Windows.Forms.DockStyle.Fill;
			this.lblCurrResult.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.lblCurrResult.Location = new System.Drawing.Point(377, 36);
			this.lblCurrResult.Name = "lblCurrResult";
			this.lblCurrResult.Size = new System.Drawing.Size(49, 36);
			this.lblCurrResult.TabIndex = 13;
			this.lblCurrResult.Text = "EUR";
			this.lblCurrResult.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// lblRonResult
			// 
			this.lblRonResult.AutoSize = true;
			this.lblRonResult.Dock = System.Windows.Forms.DockStyle.Fill;
			this.lblRonResult.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.lblRonResult.Location = new System.Drawing.Point(377, 0);
			this.lblRonResult.Name = "lblRonResult";
			this.lblRonResult.Size = new System.Drawing.Size(49, 36);
			this.lblRonResult.TabIndex = 14;
			this.lblRonResult.Text = "RON";
			this.lblRonResult.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// btnTrend
			// 
			this.btnTrend.Enabled = false;
			this.btnTrend.Location = new System.Drawing.Point(357, 3);
			this.btnTrend.Name = "btnTrend";
			this.btnTrend.Size = new System.Drawing.Size(75, 22);
			this.btnTrend.TabIndex = 7;
			this.btnTrend.Text = "Trend";
			this.btnTrend.UseVisualStyleBackColor = true;
			this.btnTrend.Click += new System.EventHandler(this.btnTrend_Click);
			// 
			// CursForm
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(435, 106);
			this.Controls.Add(this.tableLayoutPanel1);
			this.MaximizeBox = false;
			this.Name = "CursForm";
			this.Text = "BNR Converter";
			this.Load += new System.EventHandler(this.CursForm_Load);
			this.tableLayoutPanel1.ResumeLayout(false);
			this.tableLayoutPanel1.PerformLayout();
			this.tableLayoutPanel2.ResumeLayout(false);
			this.tableLayoutPanel2.PerformLayout();
			this.ResumeLayout(false);

		}

		#endregion

		private System.Windows.Forms.DateTimePicker dateCurs;
		private System.Windows.Forms.ComboBox cbCurr;
		private System.Windows.Forms.Label lblCurs;
		private System.Windows.Forms.TableLayoutPanel tableLayoutPanel1;
		private System.Windows.Forms.TableLayoutPanel tableLayoutPanel2;
		private System.Windows.Forms.Label lblCurrValue;
		private System.Windows.Forms.TextBox tbRonValue;
		private System.Windows.Forms.TextBox tbCurrValue;
		private System.Windows.Forms.TextBox tbRonResult;
		private System.Windows.Forms.Label lblRonValue;
		private System.Windows.Forms.TextBox tbCurrResult;
		private System.Windows.Forms.Label lblCurrResult;
		private System.Windows.Forms.Label lblRonResult;
		private System.Windows.Forms.Button btnGet;
		private System.Windows.Forms.Button btnTrend;
	}
}

