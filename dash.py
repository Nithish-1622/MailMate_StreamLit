Current email context:
{email_context}
Total emails in system: {len(emails)}
Provide helpful, concise responses about the user's emails. Be professional and informative."""
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm currently unable to process your request. Please ensure your AI service is configured correctly. Error: {str(e)}"
def create_modern_metrics_dashboard(emails):
    st.header("📊 Email Metrics Dashboard")
    if not emails:
        st.warning("No email data available")
        return
    total_emails = len(emails)
    high_priority = len([e for e in emails if e.get('priority_label') == 'High'])
    medium_priority = len([e for e in emails if e.get('priority_label') == 'Medium'])
    low_priority = len([e for e in emails if e.get('priority_label') == 'Low'])
    categories = {}
    for email in emails:
        category = email.get('category', 'General')
        categories[category] = categories.get(category, 0) + 1
    avg_priority = np.mean([e.get('priority_score', 0) for e in emails])
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📧 Total Emails", total_emails)
    with col2:
        st.metric("🔥 High Priority", high_priority, delta=f"{high_priority/total_emails*100:.1f}%")
    with col3:
        st.metric("⚠️ Medium Priority", medium_priority, delta=f"{medium_priority/total_emails*100:.1f}%")
    with col4:
        st.metric("📝 Low Priority", low_priority, delta=f"{low_priority/total_emails*100:.1f}%")
    with col5:
        st.metric("🎯 Avg Priority", f"{avg_priority:.2f}")
def create_advanced_visualizations(emails):
    if not emails:
        st.warning("No email data available")
        return
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Email Categories")
        categories = {}
        for email in emails:
            category = email.get('category', 'General')
            categories[category] = categories.get(category, 0) + 1
        if categories:
            category_df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
            fig = px.pie(category_df, values='Count', names='Category', 
                        title='Email Distribution by Category',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("🎯 Priority Distribution")
        priorities = {}
        for email in emails:
            priority = email.get('priority_label', 'Medium')
            priorities[priority] = priorities.get(priority, 0) + 1
        if priorities:
            priority_df = pd.DataFrame(list(priorities.items()), columns=['Priority', 'Count'])
            fig = px.bar(priority_df, x='Priority', y='Count', 
                        title='Email Priority Distribution',
                        color='Priority',
                        color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#22c55e'})
            st.plotly_chart(fig, use_container_width=True)
def create_professional_analytics(emails):
    if not emails:
        return
    st.subheader("📈 Professional Email Analytics")
    email_dates = []
    priority_scores = []
    categories = []
    for email in emails:
        timestamp = email.get('timestamp')
        score = email.get('priority_score', 0)
        category = email.get('category', 'General')
        if timestamp:
            try:
                if 'T' in timestamp:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                email_dates.append(date)
                priority_scores.append(score)
                categories.append(category)
            except:
                continue
    if email_dates:
        time_df = pd.DataFrame({
            'Date': email_dates,
            'Priority Score': priority_scores,
            'Category': categories
        })
        time_df = time_df.sort_values('Date')
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(time_df, x='Date', y='Priority Score', 
                         title='Priority Scores Over Time',
                         markers=True)
            fig.update_traces(line_color='#3b82f6', marker_color='#1d4ed8')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            daily_counts = time_df.groupby([time_df['Date'].dt.date, 'Category']).size().reset_index(name='Count')
            daily_counts['Date'] = pd.to_datetime(daily_counts['Date'])
            if len(daily_counts) > 0:
                fig = px.line(daily_counts, x='Date', y='Count', color='Category',
                             title='Email Volume by Category Over Time',
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
def display_modern_email_list(emails):
    st.header("📧 Top Priority Emails")
    if not emails:
        st.warning("No emails to display")
        return
    sorted_emails = sorted(emails, key=lambda x: x.get('priority_score', 0), reverse=True)[:5]
    st.subheader("🔥 Top 5 Priority Emails")
    for i, email in enumerate(sorted_emails, 1):
        with st.expander(f"#{i} - {email.get('subject', 'No Subject')} (Priority: {email.get('priority_label', 'Medium')})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**From:** {email.get('sender', 'Unknown')}")
                st.write(f"**Date:** {email.get('timestamp', 'Unknown')}")
                st.write(f"**Category:** {email.get('category', 'General')}")
                if email.get('ai_summary'):
                    st.write("**AI Summary:**")
                    st.info(email['ai_summary'])
                content = email.get('content', email.get('body', ''))
                if content:
                    st.write("**Content Preview:**")
                    with st.container():
                        st.text_area("Content", content[:500] + "..." if len(content) > 500 else content, 
                                   height=100, disabled=True, key=f"content_{i}", label_visibility="collapsed")
            with col2:
                st.metric("Priority Score", f"{email.get('priority_score', 0):.2f}")
                st.write(f"**Sentiment:** {email.get('sentiment', 'neutral').title()}")
                if st.button(f"🔊 Read Aloud", key=f"read_{i}"):
                    try:
                        from enhanced_tts import speak_text
                        text = f"Email from {email.get('sender', 'unknown sender')}. Subject: {email.get('subject', 'no subject')}. {email.get('ai_summary', content[:200])}"
                        success = speak_text(text, async_mode=True)
                        if success:
                            st.success("🔊 Playing email...")
                        else:
                            st.error("❌ TTS not available")
                    except Exception as e:
                        st.error(f"TTS Error: {e}")
def smart_email_chatbot():
    st.header("🤖 AI Email Assistant")
    user_input = st.text_input("Ask me about your emails:", 
                              placeholder="e.g., What are my urgent emails today?")
    col1, col2 = st.columns([3, 1])
    with col2:
        send_button = st.button("Send 🚀", type="primary", use_container_width=True)
    if send_button and user_input:
        with st.spinner("🔍 Analyzing your request..."):
            try:
                emails = st.session_state.get('emails', [])
                response = get_ai_response(user_input, emails)
                st.success("Response generated!")
                with st.container():
                    st.write(f"**You:** {user_input}")
                    st.write(f"**MailMate AI:** {response}")
            except Exception as e:
                st.error(f"Error: {e}")
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Email Summary", use_container_width=True):
            emails = st.session_state.get('emails', [])
            if emails:
                total = len(emails)
                high_priority = len([e for e in emails if e.get('priority_label') == 'High'])
                categories_count = len(set(e.get('category', 'General') for e in emails))
                st.success(f"""
                📈 **Email Overview:**
                - Total emails: {total}
                - High priority: {high_priority}
                - Categories: {categories_count}
                📊 **Quick Analytics:**
                - Most common category: {most_common}
                - Average priority score: {avg_score:.2f}
                **Email Summary:**
                - Total emails: {total}
                - High priority: {high_priority}
                - Categories: {len(set(e.get('category', 'General') for e in emails))}
                **Quick Analytics:**
                - Most common category: {most_common}
                - Average priority score: {np.mean([e.get('priority_score', 0) for e in emails]):.2f}
        **Getting Started:**
        1. Run `python main.py process` to process your emails
        2. Or run `python setup_demo.py` for sample data
        3. Refresh this page to see your processed emails
