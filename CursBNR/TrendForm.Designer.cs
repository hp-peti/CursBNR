namespace CursBNR
{
	partial class TrendForm
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
			this.components = new System.ComponentModel.Container();
			this.dateBegin = new System.Windows.Forms.DateTimePicker();
			this.dateEnd = new System.Windows.Forms.DateTimePicker();
			this.lblCurrency = new System.Windows.Forms.Label();
			this.btnGet = new System.Windows.Forms.Button();
			this.boxGraph = new System.Windows.Forms.PictureBox();
			this.progress = new System.Windows.Forms.ProgressBar();
			this.timerGraph = new System.Windows.Forms.Timer(this.components);
			((System.ComponentModel.ISupportInitialize)(this.boxGraph)).BeginInit();
			this.SuspendLayout();
			// 
			// dateBegin
			// 
			this.dateBegin.Format = System.Windows.Forms.DateTimePickerFormat.Short;
			this.dateBegin.Location = new System.Drawing.Point(12, 12);
			this.dateBegin.Name = "dateBegin";
			this.dateBegin.Size = new System.Drawing.Size(100, 20);
			this.dateBegin.TabIndex = 1;
			// 
			// dateEnd
			// 
			this.dateEnd.Format = System.Windows.Forms.DateTimePickerFormat.Short;
			this.dateEnd.Location = new System.Drawing.Point(118, 12);
			this.dateEnd.Name = "dateEnd";
			this.dateEnd.Size = new System.Drawing.Size(100, 20);
			this.dateEnd.TabIndex = 2;
			// 
			// lblCurrency
			// 
			this.lblCurrency.AutoSize = true;
			this.lblCurrency.Font = new System.Drawing.Font("Trebuchet MS", 14.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
			this.lblCurrency.Location = new System.Drawing.Point(224, 10);
			this.lblCurrency.Name = "lblCurrency";
			this.lblCurrency.Size = new System.Drawing.Size(46, 24);
			this.lblCurrency.TabIndex = 8;
			this.lblCurrency.Text = "EUR";
			this.lblCurrency.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
			// 
			// btnGet
			// 
			this.btnGet.Location = new System.Drawing.Point(276, 10);
			this.btnGet.Name = "btnGet";
			this.btnGet.Size = new System.Drawing.Size(75, 23);
			this.btnGet.TabIndex = 9;
			this.btnGet.Text = "Get";
			this.btnGet.UseVisualStyleBackColor = true;
			this.btnGet.Click += new System.EventHandler(this.btnGet_Click);
			// 
			// boxGraph
			// 
			this.boxGraph.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
						| System.Windows.Forms.AnchorStyles.Left)
						| System.Windows.Forms.AnchorStyles.Right)));
			this.boxGraph.BackColor = System.Drawing.SystemColors.Window;
			this.boxGraph.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
			this.boxGraph.Location = new System.Drawing.Point(12, 40);
			this.boxGraph.Name = "boxGraph";
			this.boxGraph.Size = new System.Drawing.Size(442, 237);
			this.boxGraph.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
			this.boxGraph.TabIndex = 10;
			this.boxGraph.TabStop = false;
			this.boxGraph.Resize += new System.EventHandler(this.boxGraph_Resize);
			// 
			// progress
			// 
			this.progress.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left)
						| System.Windows.Forms.AnchorStyles.Right)));
			this.progress.Location = new System.Drawing.Point(357, 12);
			this.progress.Name = "progress";
			this.progress.Size = new System.Drawing.Size(97, 20);
			this.progress.TabIndex = 11;
			// 
			// timerGraph
			// 
			this.timerGraph.Interval = 55;
			this.timerGraph.Tick += new System.EventHandler(this.timer1_Tick);
			// 
			// TrendForm
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(467, 289);
			this.Controls.Add(this.progress);
			this.Controls.Add(this.boxGraph);
			this.Controls.Add(this.btnGet);
			this.Controls.Add(this.lblCurrency);
			this.Controls.Add(this.dateEnd);
			this.Controls.Add(this.dateBegin);
			this.Name = "TrendForm";
			this.Text = "Trend";
			this.Shown += new System.EventHandler(this.TrendForm_Shown);
			this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.TrendForm_FormClosing);
			((System.ComponentModel.ISupportInitialize)(this.boxGraph)).EndInit();
			this.ResumeLayout(false);
			this.PerformLayout();

		}

		#endregion

		private System.Windows.Forms.DateTimePicker dateBegin;
		private System.Windows.Forms.DateTimePicker dateEnd;
		private System.Windows.Forms.Label lblCurrency;
		private System.Windows.Forms.Button btnGet;
		private System.Windows.Forms.PictureBox boxGraph;
		private System.Windows.Forms.ProgressBar progress;
		private System.Windows.Forms.Timer timerGraph;
	}
}